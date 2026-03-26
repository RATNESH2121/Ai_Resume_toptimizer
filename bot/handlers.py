"""
Telegram Bot Handlers.
Manages the full conversation flow:
  /start → Upload JD → Upload Resume → Score → Choose Template → Download PDF
"""

import os
import io
import json
import logging
import tempfile

import pdfplumber
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ChatAction

# Import our core utilities
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django for standalone bot usage
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_optimizer.settings')
import django
django.setup()

from core.utils.pdf_extractor import extract_text_from_file, extract_text_from_string
from core.utils.ai_scorer import analyze_resume
from core.utils.pdf_generator import generate_resume_pdf

logger = logging.getLogger(__name__)

# Conversation states
AWAITING_JD = 1
AWAITING_RESUME = 2
AWAITING_TEMPLATE = 3


def get_score_emoji(score):
    if score >= 8: return '🔥'
    if score >= 6: return '✅'
    if score >= 4: return '⚠️'
    return '❌'


def format_score_message(data):
    score = float(data.get('ats_score', 0))
    match_pct = data.get('match_percent', 0)
    opt_score = float(data.get('optimized_score', 0))
    role = data.get('role_detected', 'Not detected')
    breakdown = data.get('breakdown', {})
    missing = data.get('missing_keywords', [])
    feedback = data.get('feedback', [])
    strengths = data.get('strengths', [])

    emoji = get_score_emoji(score)

    msg = f"""
{emoji} *ATS SCORE ANALYSIS* {emoji}

━━━━━━━━━━━━━━━━━━━━
🏆 *Score: {score:.1f} / 10*
📊 *Match: {match_pct}%*
🎯 *Role: {role}*
━━━━━━━━━━━━━━━━━━━━

📈 *Score Breakdown:*
├ 💻 Skills Match: `{breakdown.get('skills_match', 0)}/40`
├ 💼 Experience: `{breakdown.get('experience_relevance', 0)}/30`  
├ 🔍 ATS Keywords: `{breakdown.get('keywords_ats', 0)}/20`
└ 📐 Structure: `{breakdown.get('structure_format', 0)}/10`
"""

    if strengths:
        msg += "\n💪 *Your Strengths:*\n"
        for s in strengths[:3]:
            msg += f"  ✅ {s}\n"

    if missing:
        msg += f"\n❌ *Missing Keywords:*\n`{', '.join(missing[:10])}`\n"

    if feedback:
        msg += "\n💡 *Specific Improvements:*\n"
        for i, f in enumerate(feedback[:5], 1):
            msg += f"  {i}. {f}\n"

    msg += f"""
━━━━━━━━━━━━━━━━━━━━
📈 After Optimization: *{score:.1f}/10 → {opt_score:.1f}/10* 🚀
━━━━━━━━━━━━━━━━━━━━
"""
    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    context.user_data.clear()

    welcome = """
🚀 *Welcome to ResumeAI Bot!*

I'll analyze your resume against a Job Description and:

📊 Give you an *ATS score out of 10*
💡 Provide *specific improvement tips*  
✍️ Generate an *optimized resume*
📄 Send it as a *downloadable PDF*

━━━━━━━━━━━━━━━━━━━━
*Let's start!*

Please send me the *Job Description* 📋
_(PDF file or paste the text)_
"""

    await update.message.reply_text(
        welcome,
        parse_mode='Markdown'
    )
    return AWAITING_JD


async def receive_jd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle JD upload (file or text)."""
    jd_text = ""

    if update.message.document:
        # File uploaded
        await update.message.reply_text("⏳ Reading Job Description...")
        file = await update.message.document.get_file()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            await file.download_to_drive(tmp.name)
            with open(tmp.name, 'rb') as f:
                try:
                    jd_text = extract_text_from_file(f, update.message.document.file_name)
                except Exception as e:
                    await update.message.reply_text(f"❌ Could not read file: {str(e)}\nPlease try pasting the text directly.")
                    return AWAITING_JD
        os.unlink(tmp.name)
    elif update.message.text:
        jd_text = update.message.text.strip()
        if jd_text.startswith('/'):
            await update.message.reply_text("Please send the Job Description text or PDF file.")
            return AWAITING_JD

    if len(jd_text) < 50:
        await update.message.reply_text("⚠️ JD seems too short. Please send a complete Job Description.")
        return AWAITING_JD

    context.user_data['jd_text'] = jd_text

    await update.message.reply_text(
        f"✅ *Job Description received!*\n"
        f"📋 Length: {len(jd_text)} characters\n\n"
        f"Now send me your *Resume* 📝\n_(PDF file or paste the text)_",
        parse_mode='Markdown'
    )
    return AWAITING_RESUME


async def receive_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Resume upload (file or text)."""
    resume_text = ""

    if update.message.document:
        await update.message.reply_chat_action(ChatAction.TYPING)
        file = await update.message.document.get_file()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            await file.download_to_drive(tmp.name)
            with open(tmp.name, 'rb') as f:
                try:
                    resume_text = extract_text_from_file(f, update.message.document.file_name)
                except Exception as e:
                    await update.message.reply_text(f"❌ Could not read file: {str(e)}\nPlease try pasting the text directly.")
                    return AWAITING_RESUME
        os.unlink(tmp.name)
    elif update.message.text:
        resume_text = update.message.text.strip()
        if resume_text.startswith('/'):
            await update.message.reply_text("Please send your resume text or PDF file.")
            return AWAITING_RESUME

    if len(resume_text) < 100:
        await update.message.reply_text("⚠️ Resume seems too short. Please send a complete resume.")
        return AWAITING_RESUME

    context.user_data['resume_text'] = resume_text

    # Start analysis
    analyzing_msg = await update.message.reply_text(
        "🧠 *Analyzing your resume with AI...*\n\n"
        "⏳ Matching keywords\n"
        "⏳ Scoring with Gemini AI\n"
        "⏳ Generating improvements\n",
        parse_mode='Markdown'
    )

    await update.message.reply_chat_action(ChatAction.TYPING)

    try:
        jd_text = context.user_data['jd_text']
        result = analyze_resume(jd_text, resume_text)
        context.user_data['analysis_result'] = result

        # Send score message
        score_msg = format_score_message(result)
        await analyzing_msg.edit_text(score_msg, parse_mode='Markdown')

        # Ask about PDF generation
        keyboard = [
            [InlineKeyboardButton("✅ Yes, generate optimized resume!", callback_data='generate_yes')],
            [InlineKeyboardButton("❌ No thanks", callback_data='generate_no')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🚀 *Generate your optimized resume PDF?*\n"
            "_AI will rewrite your resume to maximize ATS score_",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return AWAITING_TEMPLATE

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        await analyzing_msg.edit_text(
            f"❌ *Analysis failed:* {str(e)}\n\nPlease try again with /start",
            parse_mode='Markdown'
        )
        return ConversationHandler.END


async def handle_template_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle generate PDF confirmation and template selection."""
    query = update.callback_query
    await query.answer()

    if query.data == 'generate_no':
        await query.edit_message_text("👍 No problem! Use /start to analyze another resume.")
        return ConversationHandler.END

    if query.data == 'generate_yes':
        # Show template options
        keyboard = [
            [InlineKeyboardButton("🎨 Modern Clean (1-Page)", callback_data='template_modern')],
            [InlineKeyboardButton("🏢 Corporate Classic (2-Page)", callback_data='template_corporate')],
            [InlineKeyboardButton("📦 Get Both PDFs!", callback_data='template_both')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎨 *Choose your resume template:*",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return AWAITING_TEMPLATE

    if query.data.startswith('template_'):
        template = query.data.replace('template_', '')
        result = context.user_data.get('analysis_result', {})
        resume_data = result.get('optimized_resume')

        if not resume_data:
            await query.edit_message_text(
                "⚠️ Optimized resume data not available.\n"
                "Please try again with /start"
            )
            return ConversationHandler.END

        await query.edit_message_text("⏳ *Generating your optimized PDF...*", parse_mode='Markdown')

        try:
            if template == 'both':
                # Send both PDFs
                for tpl, label in [('modern', 'Modern Clean'), ('corporate', 'Corporate Classic')]:
                    pdf_bytes = generate_resume_pdf(resume_data, template=tpl)
                    pdf_io = io.BytesIO(pdf_bytes)
                    pdf_io.name = f'optimized_resume_{tpl}.pdf'
                    await query.message.reply_document(
                        document=pdf_io,
                        filename=f'optimized_resume_{tpl}.pdf',
                        caption=f"📄 *{label} Template*",
                        parse_mode='Markdown'
                    )
            else:
                pdf_bytes = generate_resume_pdf(resume_data, template=template)
                pdf_io = io.BytesIO(pdf_bytes)
                pdf_io.name = f'optimized_resume_{template}.pdf'
                await query.message.reply_document(
                    document=pdf_io,
                    filename=f'optimized_resume_{template}.pdf',
                    caption=f"📄 Your optimized resume — *{template.title()} template*",
                    parse_mode='Markdown'
                )

            old_score = float(result.get('ats_score', 0))
            new_score = float(result.get('optimized_score', 0))

            await query.message.reply_text(
                f"✅ *Done! Your optimized resume is ready!*\n\n"
                f"📈 Score improvement: *{old_score:.1f}/10 → {new_score:.1f}/10*\n\n"
                f"You're all set! Use /start to optimize another resume 🚀",
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            await query.message.reply_text(
                f"❌ PDF generation failed: {str(e)}\nPlease try again with /start"
            )

        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command."""
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. Use /start to begin again.")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📖 *ResumeAI Bot Help*\n\n"
        "/start — Start a new analysis\n"
        "/cancel — Cancel current session\n"
        "/help — Show this help\n\n"
        "*Supported file formats:* PDF, DOCX, TXT\n"
        "*Supports:* Any job role — Engineering, MBA, Design, etc.",
        parse_mode='Markdown'
    )
