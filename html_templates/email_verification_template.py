from config.settings import settings

def email_verification_template(state):
    """
    Returns the email verification HTML template.

    Args:
        state (dict): Contains userName, verifyLink, and willExpireIn.

    Returns:
        str: HTML content for email verification.
    """
    userName = state.get("userName")
    verifyLink = state.get("verifyLink")
    willExpireIn = state.get("willExpireIn")

    facebook = "https://img.icons8.com/?size=100&id=8818&format=png&color=1A1A1A"
    instagram = "https://img.icons8.com/?size=100&id=phOKFKYpe00C&format=png&color=1A1A1A"
    twitter = "https://img.icons8.com/?size=100&id=ZOFC5nSr215Y&format=png&color=1A1A1A"

    return f"""
    <!doctype html>
    <html lang="en">
        <head>
            <title>{settings.hinata_host} - Email Verification</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style type="text/css">
                body {{
                    margin: 0;
                    padding: 0;
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                    background-color: #F5F7FB;
                    font-family: 'Inter', Arial, sans-serif;
                    color: #1F2A47;
                }}
                table, td {{
                    border-collapse: collapse;
                    mso-table-lspace: 0pt;
                    mso-table-rspace: 0pt;
                }}
                img {{
                    border: 0;
                    height: auto;
                    line-height: 100%;
                    outline: none;
                    text-decoration: none;
                    -ms-interpolation-mode: bicubic;
                    filter: invert(70%);
                }}
                p {{
                    display: block;
                    margin: 0;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 40px auto;
                    background: #FFFFFF;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    padding: 0 15px;
                }}
                .header {{
                    background: #7D4CDB;
                    padding: 30px 20px;
                    text-align: center;
                    color: white;
                }}
                .header h3 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                    color: #FFFFFF;
                }}
                .content {{
                    padding: 30px;
                    line-height: 1.6;
                }}
                .button-container {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #7D4CDB;
                    color: white;
                    padding: 14px 28px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 18px;
                    transition: all 0.3s ease;
                    width: 80%;
                    max-width: 250px;
                    box-sizing: border-box;
                }}
                .button:hover {{
                    background-color: #6B3FCB;
                    transform: translateY(-2px);
                }}
                .button span {{
                    color: #FFFFFF;
                }}
                .alt-link {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #1F2A47;
                    word-wrap: break-word;
                }}
                .footer {{
                    background-color: #F5F7FB;
                    color: #1F2A47;
                    text-align: center;
                    padding: 20px;
                    font-size: 12px;
                }}
                .social-icons {{
                    margin-top: 20px;
                }}
                .social-icons a {{
                    display: inline-block;
                    margin: 0 10px;
                    transition: transform 0.3s ease;
                }}
                .social-icons a:hover {{
                    transform: scale(1.2);
                }}
                .social-icons img {{
                    width: 20px;
                    height: 20px;
                }}
                @media only screen and (max-width: 600px) {{
                    .header h3 {{
                        font-size: 20px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .button {{
                        padding: 12px 24px;
                        font-size: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h3>Email Verification</h3>
                </div>
                <div class="content">
                    <p>Hi {userName},</p>
                    <p>You recently created your {settings.hinata_host} account. Use the button below to verify your email.</p>
                    <p>This verification link is only valid for the next {willExpireIn} minutes.</p>
                    <div class="button-container">
                        <a href="{verifyLink}" class="button" target="_blank" rel="noopener noreferrer"><span>Click here</span></a>
                    </div>
                    <p class="alt-link">Or, if you’re having trouble with the button above, copy and paste the URL below into your web browser.</p>
                    <p class="alt-link"><a href="{verifyLink}" style="color: #7D4CDB;">{verifyLink}</a></p>
                </div>
                <div class="footer">
                    <p>If you did not expect this request, please ignore this mail.</p>
                    <div class="social-icons">
                        <a href="https://www.facebook.com/gofynd/" target="_blank">
                            <img src="{facebook}" alt="Facebook">
                        </a>
                        <a href="https://twitter.com/GoFynd" target="_blank">
                            <img src="{twitter}" alt="Twitter">
                        </a>
                        <a href="https://www.instagram.com/gofynd/" target="_blank">
                            <img src="{instagram}" alt="Instagram">
                        </a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
