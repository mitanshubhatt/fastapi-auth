def invitation_template(state):
    """
    Returns the email verification HTML template.

    Args:
        state (dict): Contains userName, verifyLink, and willExpireIn.

    Returns:
        str: HTML content for email verification.
    """
    verifyLink = state.get("verifyLink")

    facebook = "https://img.icons8.com/?size=100&id=8818&format=png&color=1A1A1A"
    instagram = "https://img.icons8.com/?size=100&id=phOKFKYpe00C&format=png&color=1A1A1A"
    twitter = "https://img.icons8.com/?size=100&id=ZOFC5nSr215Y&format=png&color=1A1A1A"

    return f"""
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invitation to Join Fynix</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        body {{
            font-family: 'Inter', Arial, sans-serif;
            background-color: #F5F7FB;
            margin: 0;
            padding: 0;
            color: #1F2A47;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #FFFFFF;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
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
        }}
        .button span {{
            color: #FFFFFF; /* Ensures the button text is white and visible */
          }}
        .button:hover {{
            background-color: #6B3FCB;
            transform: translateY(-2px);
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h3>Invitation to Join Fynix</h3>
        </div>
        <div class="content">
            <p>Dear User,</p>
            <p>You have been invited to join the Fynix platform. We are thrilled to extend this warm invitation to you.</p>
            <p>Click the button below to complete your registration. Please note that this invitation link is valid only for the next 24 hours.</p>
            <div class="button-container">
                <a href="${verifyLink}" class="button" target="_blank" rel="noopener noreferrer"><span>Join</span></a>
            </div>
            <p class="alt-link">Or, if you’re having trouble with the button above, copy and paste the URL below into your web browser.</p>
            <p class="alt-link"><a href="${verifyLink}" style="color: #7D4CDB;">${verifyLink}</a></p>
        </div>
        <div class="footer">
            <p>If you did not expect this invitation, please disregard this email.</p>
            <div class="social-icons">
                <a href="https://www.facebook.com/gofynd/" target="_blank">
                    <img src="${facebook}" alt="Facebook">
                </a>
                <a href="https://twitter.com/GoFynd" target="_blank">
                    <img src="${twitter}" alt="Twitter">
                </a>
                <a href="https://www.instagram.com/gofynd/" target="_blank">
                    <img src="${instagram}" alt="Instagram">
                </a>
            </div>
        </div>
    </div>
</body>
</html>
    """
