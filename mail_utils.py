from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer


def send_email(mail_instance, subject, recipients, html_body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail_instance.send(msg)

def send_verification_email(mail_instance, user):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(user.email)
    
    verification_url = url_for('auth.verify_email', token=token, _external=True)
    
    html = f"""
    <h1>Bienvenue sur SignalAlert !</h1>
    <p>Merci de vous être inscrit. Veuillez cliquer sur le lien ci-dessous pour vérifier votre adresse email :</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>Ce lien expirera dans 1 heure.</p>
    <br>
    <p>L'équipe SignalAlert</p>
    """
    
    send_email(mail_instance, 'Vérifiez votre email - SignalAlert', [user.email], html)

def send_password_reset_email(mail_instance, user):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(user.email)
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    html = f"""
    <h1>Réinitialisation de votre mot de passe</h1>
    <p>Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous :</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>Si vous n'avez pas fait cette demande, ignorez simplement cet email.</p>
    <p>Ce lien expirera dans 1 heure.</p>
    <br>
    <p>L'équipe SignalAlert</p>
    """
    
    send_email(mail_instance, 'Réinitialisation de mot de passe - SignalAlert', [user.email], html)

def send_match_notification(mail_instance, user, signalement, match):
    html = f"""
    <h1>Nouvelle correspondance trouvée !</h1>
    <p>Un signalement pourrait correspondre à votre annonce "{signalement.title}".</p>
    <p>Type de correspondance : {match.similarity_score}%</p>
    <p><a href="{url_for('main.signalement_detail', id=signalement.id, _external=True)}">
        Voir la correspondance
    </a></p>
    <br>
    <p>L'équipe SignalAlert</p>
    """
    
    send_email(mail_instance, 'Nouvelle correspondance - SignalAlert', [user.email], html)