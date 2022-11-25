import mechanize
import os

class LoginException():
    Exception('Login failed.')


class PostException():
    Exception('Could not post message.')


def start_mechanize_browser() -> mechanize.Browser:
    """Start a browser session using the mechanize package."""

    HEAD_UA = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'
    HEAD_ACC = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('user-agent', HEAD_UA),
                          ('accept', HEAD_ACC)]
    return browser


def login_to_forum(browser: mechanize.Browser) -> mechanize.Browser:
    """Login to forum"""

    browser.open(os.getenv('FORUM_LOGIN_URL'))

    # Select first form(login form) and set values to the credentials
    browser.form = list(browser.forms())[1]
    browser["vb_login_username"] = os.getenv('FORUM_ACCOUNT')
    browser["vb_login_password"] = os.getenv('FORUM_PASSWORD')
    try:
        browser.submit()
        print(f"Successfully logged in to {os.getenv('FORUM_BASE_URL')} with username {os.getenv('FORUM_ACCOUNT')}.")
    except:
        raise LoginException()
        
    return browser


def post_message(browser: mechanize.Browser, message:str) -> None:
    """Post message to forum"""

    try:
        browser.open(os.getenv('FORUM_TOPIC_URL'))
        browser.select_form('quick_reply')
        browser['message'] = message
        browser.submit()
        print('Posted message.')
    except:
        raise PostException()


def post_results_to_forum(message: str) -> None:

    print(message)
    browser = start_mechanize_browser()
    browser = login_to_forum(browser)
    post_message(browser, message)
    
