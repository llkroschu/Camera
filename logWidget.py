class LogWidget:
    """Enable logging to logfile and LogWidget"""

    @staticmethod
    def initialize(info_box):
        LogWidget.log_text = ["", ""]
        LogWidget.info_box = info_box

    @staticmethod
    def set_info(text: str):
        try:
            LogWidget.log_text = text
            LogWidget.info_box.setText(LogWidget.log_text)
        except:
            pass

    @staticmethod
    def remove():
        try:
            LogWidget.text = ""
            LogWidget.info_box.setText(LogWidget.text)
        except:
            pass