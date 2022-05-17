WEBVPN_BASE_URL = "https://webvpn.bupt.edu.cn"
WEBVPN_LOGIN_URL = f"{WEBVPN_BASE_URL}/login"
WEBVPN_DO_LOGIN_URL = f"{WEBVPN_BASE_URL}/do-login"
WEBVPN_USER_INFO_URL = f'{WEBVPN_BASE_URL}/user/info'

JWGL_BASE_URL = "https://jwgl.bupt.edu.cn"
JWGL_JSXSD_URL = f"{JWGL_BASE_URL}/jsxsd"
JWGL_FRAME_URL = f"{JWGL_JSXSD_URL}/framework"
JWGL_LOGON_DO_URL = f"{JWGL_BASE_URL}/Logon.do?method=logon"
JWGL_LOGIN_TO_XK_URL = f"{JWGL_JSXSD_URL}/xk/LoginToXk"
JWGL_XS_MAIN_URL = f"{JWGL_FRAME_URL}/xsMain.jsp"
JWGL_KB_URL = f"{JWGL_FRAME_URL}/main_index_loadkb.jsp"
JWGL_XS_MAIN_NEW_URL = f"{JWGL_FRAME_URL}/xsMain_new.jsp?t1=1"

KTP_BASE_URL = "https://www.ketangpai.com"
KTP_API_BASE_URL = "https://openapiv5.ketangpai.com/"  # This contains '/' at the end.
KTP_WECHAT_QRCODE_URL = f"{KTP_API_BASE_URL}/wechat/login"
KTP_CHECK_WECHAT_LOGIN_URL = f"{KTP_API_BASE_URL}/UserApi/checkWechatCode"
KTP_LOGIN_URL = f"{KTP_API_BASE_URL}/UserApi/login"
KTP_FIGURE_CODE_URL = f"{KTP_API_BASE_URL}/UserApi/getFigureCode"
KTP_SEND_CODE_URL = f"{KTP_API_BASE_URL}/UserApi/sendCode"
KTP_LOGIN_PHONE_URL = f"{KTP_API_BASE_URL}/UserApi/loginByMobile"
