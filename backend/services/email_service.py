"""
É FESTA — Serviço de E-mail
Arquivo: backend/services/email_service.py
Envia e-mails transacionais via SMTP
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import settings
import logging

logger = logging.getLogger(__name__)


def _enviar_email(destinatario: str, assunto: str, corpo_html: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"]    = settings.SMTP_FROM
        msg["To"]      = destinatario
        msg.attach(MIMEText(corpo_html, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, destinatario, msg.as_string())

        logger.info(f"E-mail enviado para {destinatario}: {assunto}")
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}")


def enviar_email_boas_vindas(email: str, nome: str):
    corpo = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#E8163C;padding:32px;text-align:center;">
        <h1 style="color:white;font-size:2rem;margin:0;">🎉 É Festa</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#1A0A2E;">Bem-vindo(a), {nome}! 🎊</h2>
        <p>Sua conta foi criada com sucesso no <strong>É Festa</strong>, o maior marketplace de festas e eventos do Brasil.</p>
        <p>Agora você pode buscar fornecedores, salvar favoritos e avaliar profissionais gratuitamente.</p>
        <div style="text-align:center;margin-top:24px;">
          <a href="{settings.APP_URL}" style="background:#E8163C;color:white;padding:14px 28px;border-radius:100px;text-decoration:none;font-weight:bold;">Começar a buscar →</a>
        </div>
      </div>
      <div style="background:#f5f5f5;padding:16px;text-align:center;font-size:12px;color:#999;">
        © 2025 É Festa · <a href="{settings.APP_URL}/privacidade" style="color:#999;">Política de Privacidade</a>
      </div>
    </div>
    """
    _enviar_email(email, "Bem-vindo(a) ao É Festa! 🎉", corpo)


def enviar_email_reset_senha(email: str, nome: str, link: str):
    corpo = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#E8163C;padding:32px;text-align:center;">
        <h1 style="color:white;">🎉 É Festa</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#1A0A2E;">Redefinição de Senha</h2>
        <p>Olá, {nome}! Recebemos uma solicitação para redefinir sua senha.</p>
        <p>Clique no botão abaixo para criar uma nova senha. Este link expira em <strong>2 horas</strong>.</p>
        <div style="text-align:center;margin:24px 0;">
          <a href="{link}" style="background:#E8163C;color:white;padding:14px 28px;border-radius:100px;text-decoration:none;font-weight:bold;">Redefinir minha senha</a>
        </div>
        <p style="color:#999;font-size:13px;">Se você não solicitou isso, ignore este e-mail. Sua senha permanece a mesma.</p>
      </div>
    </div>
    """
    _enviar_email(email, "Redefinição de senha — É Festa", corpo)


def enviar_email_aprovacao_profissional(email: str, nome: str):
    corpo = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#E8163C;padding:32px;text-align:center;">
        <h1 style="color:white;">🎉 É Festa</h1>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#1A0A2E;">✅ Seu perfil foi aprovado!</h2>
        <p>Parabéns, {nome}! Seu perfil profissional no É Festa foi aprovado e já está visível para milhares de usuários.</p>
        <div style="text-align:center;margin:24px 0;">
          <a href="{settings.APP_URL}/painel-profissional" style="background:#E8163C;color:white;padding:14px 28px;border-radius:100px;text-decoration:none;font-weight:bold;">Acessar meu painel</a>
        </div>
      </div>
    </div>
    """
    _enviar_email(email, "✅ Perfil aprovado — É Festa", corpo)
