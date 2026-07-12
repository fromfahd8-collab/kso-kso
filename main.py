# main.py - KSO Download Turbo Ultra V1.0 PRO
# برمجة: عبد الله و عبد الرحمن هاني [KSO]
# جميع الحقوق محفوظة © 2026

import sys
import json
import os
import subprocess
import threading
import time
import datetime
import webbrowser
import queue
import shutil
import csv
import argparse
import hashlib
import tempfile
from typing import List, Optional
from pathlib import Path

# المكتبات الأساسية
import keyboard
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from plyer import notification
import yt_dlp
import speedtest_cli

# مكتبات إضافية للتشفير والمراقبة
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import psutil
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    psutil = None

# ---------- Constants ----------
CONFIG_FILE = "config.json"
LANG_FILE = "lang.json"
HISTORY_FILE = "downloads_history.json"
MAX_LIMIT = 1000000
VERSION = "V1.0 PRO"
AUTHORS = "عبد الله و عبد الرحمن هاني [KSO]"

# ---------- Default language ----------
DEFAULT_LANG = {
    "ar": {
        "title": f"KSO Download Turbo Ultra {VERSION}",
        "quality": "الجودة:",
        "path": "المسار",
        "speed": "سرعة ذكية",
        "count": "العدد:",
        "browser": "المتصفح",
        "shutdown": "اغلاق الجهاز عند الانتهاء",
        "about": "حول",
        "download_q": "هل تريد تحميل هذا الرابط؟",
        "search": "ابحث في يوتيوب...",
        "load_more": "تحميل المزيد",
        "schedule": "جدولة",
        "speed_limit": "حد السرعة (KB/s)",
        "downloads": "التحميلات",
        "name": "الاسم",
        "progress": "التقدم %",
        "speed_dl": "السرعة",
        "size": "الحجم",
        "remaining": "الوقت المتبقي",
        "status": "الحالة",
        "pause": "ايقاف مؤقت",
        "resume": "استكمال",
        "delete": "حذف",
        "convert_to_mp3": "تحويل الى MP3",
        "convert_to_720p": "تحويل الى 720p",
        "cut_30s": "قص اول 30 ثانية",
        "super_compress": "الضغط الخارق",
        "study": "المذاكرة",
        "search_course": "ابحث عن كورس + اسم المادة...",
        "create_folder": "انشاء مجلد",
        "download_playlist": "تحميل كل البلاي ليست",
        "history_search": "بحث في السجل...",
        "re_download": "اعادة تحميل",
        "password": "كلمة السر",
        "language": "اللغة",
        "auto_capture": "تم العثور على فيديو. هل تريد اضافته للتحميل؟",
        "enter_password": "ادخل كلمة السر",
        "wrong_password": "كلمة سر خاطئة",
        "downloading": "جاري التحميل...",
        "finished": "تم الانتهاء",
        "paused": "متوقف مؤقت",
        "error": "خطأ",
        "pending": "في الانتظار",
        "new_password": "كلمة السر الجديدة",
        "save_password": "حفظ كلمة السر",
        "password_saved": "تم حفظ كلمة السر",
        "ffmpeg_not_found": "برجاء تثبيت FFmpeg",
        "ffmpeg_link": "تحميل FFmpeg من: https://ffmpeg.org/download.html",
        "auto_compress": "الضغط التلقائي",
        "compressing": "جاري الضغط...",
        "compressed": "تم الضغط",
        "auto_compress_stopped": "الضغط التلقائي متوقف - FFmpeg غير مثبت",
        "auto_compress_failed": "فشل الضغط التلقائي",
        "manual_threads": "اقصى خيوط يدوي",
        "smart_mode": "الوضع الذكي للخيوط",
        "file_deleted": "تم حذف الملف الاصلي لتوفير المساحة",
        "playlist_title": "اختر فيديوهات البلاي ليست",
        "download_selected": "تحميل المحدد",
        "download_all": "تحميل الكل",
        "loading_playlist": "جاري تحميل قائمة البلاي ليست...",
        "tab_all": "الكل",
        "tab_videos": "فيديوهات",
        "tab_playlists": "قوائم تشغيل",
        "tab_shorts": "شورتس",
        "proxy": "وكيل (Proxy)",
        "clear_cache": "مسح الكاش",
        "backup": "نسخ احتياطي",
        "restore": "استعادة",
        "export_csv": "تصدير CSV",
        "filter": "فلترة:",
        "filter_all": "الكل",
        "filter_finished": "مكتمل",
        "filter_downloading": "جاري",
        "filter_error": "فشل",
        "resources": "الرام: {ram} MB | المعالج: {cpu}%",
        "compress_mode": "وضع الضغط:",
        "mode_fast": "سريع",
        "mode_balanced": "متوازن",
        "mode_max": "اقصى ضغط",
        "delete_original": "حذف الاصلي",
        "welcome": "مرحباً بك في KSO Downloader!",
        "welcome_text": "هذا البرنامج مصمم لمساعدتك في تحميل الفيديوهات والملفات بسرعة فائقة.\n\nللبدء، ابحث عن فيديو في يوتيوب أو الصق رابطاً في شريط العناوين.",
        "download_channel": "تحميل القناة",
        "download_live": "تحميل البث المباشر",
        "preview": "معاينة",
        "download_page": "تحميل الصفحة",
        "clear_temp": "تنظيف الملفات المؤقتة",
        "check_md5": "فحص MD5",
        "no_duplicate": "منع التكرار",
        "organize": "تنظيم حسب النوع",
        "drag_drop": "اسحب الرابط هنا"
    },
    "en": {
        "title": f"KSO Download Turbo Ultra {VERSION}",
        "quality": "Quality:",
        "path": "Path",
        "speed": "Smart Speed",
        "count": "Parallel:",
        "browser": "Browser",
        "shutdown": "Shutdown PC when done",
        "about": "About",
        "download_q": "Download this link?",
        "search": "Search YouTube...",
        "load_more": "Load More",
        "schedule": "Schedule",
        "speed_limit": "Speed limit (KB/s)",
        "downloads": "Downloads",
        "name": "Name",
        "progress": "Progress %",
        "speed_dl": "Speed",
        "size": "Size",
        "remaining": "Remaining",
        "status": "Status",
        "pause": "Pause",
        "resume": "Resume",
        "delete": "Delete",
        "convert_to_mp3": "Convert to MP3",
        "convert_to_720p": "Convert to 720p",
        "cut_30s": "Cut first 30s",
        "super_compress": "Super Compress",
        "study": "Study",
        "search_course": "Search course + subject...",
        "create_folder": "Create Folder",
        "download_playlist": "Download Full Playlist",
        "history_search": "Search history...",
        "re_download": "Re-download",
        "password": "Password",
        "language": "Language",
        "auto_capture": "Video found. Add to downloads?",
        "enter_password": "Enter password",
        "wrong_password": "Wrong password",
        "downloading": "Downloading...",
        "finished": "Finished",
        "paused": "Paused",
        "error": "Error",
        "pending": "Pending",
        "new_password": "New Password",
        "save_password": "Save Password",
        "password_saved": "Password saved",
        "ffmpeg_not_found": "Please install FFmpeg",
        "ffmpeg_link": "Download FFmpeg from: https://ffmpeg.org/download.html",
        "auto_compress": "Auto Compress",
        "compressing": "Compressing...",
        "compressed": "Compressed",
        "auto_compress_stopped": "Auto compress stopped - FFmpeg not installed",
        "auto_compress_failed": "Auto compress failed",
        "manual_threads": "Max Manual Threads",
        "smart_mode": "Smart Thread Mode",
        "file_deleted": "Original file deleted to save space",
        "playlist_title": "Select Playlist Videos",
        "download_selected": "Download Selected",
        "download_all": "Download All",
        "loading_playlist": "Loading playlist...",
        "tab_all": "All",
        "tab_videos": "Videos",
        "tab_playlists": "Playlists",
        "tab_shorts": "Shorts",
        "proxy": "Proxy",
        "clear_cache": "Clear Cache",
        "backup": "Backup",
        "restore": "Restore",
        "export_csv": "Export CSV",
        "filter": "Filter:",
        "filter_all": "All",
        "filter_finished": "Finished",
        "filter_downloading": "Downloading",
        "filter_error": "Error",
        "resources": "RAM: {ram} MB | CPU: {cpu}%",
        "compress_mode": "Compress Mode:",
        "mode_fast": "Fast",
        "mode_balanced": "Balanced",
        "mode_max": "Max",
        "delete_original": "Delete original",
        "welcome": "Welcome to KSO Downloader!",
        "welcome_text": "This program helps you download videos and files at super speed.\n\nTo start, search for a video on YouTube or paste a link in the address bar.",
        "download_channel": "Download Channel",
        "download_live": "Download Live",
        "preview": "Preview",
        "download_page": "Download Page",
        "clear_temp": "Clear Temp Files",
        "check_md5": "Check MD5",
        "no_duplicate": "No Duplicate",
        "organize": "Organize by Type",
        "drag_drop": "Drag & Drop link here"
    }
}

# ---------- Smart speed functions ----------
def test_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        return round(st.download() / 1024 / 1024, 1)
    except:
        return 25.0

def get_smart_threads(total_files=1, smart_mode=True, manual_threads=32):
    if smart_mode:
        speed = test_speed()
        if speed <= 10:
            total_threads = 16
        elif speed <= 30:
            total_threads = 32
        elif speed <= 100:
            total_threads = 64
        elif speed <= 500:
            total_threads = 100
        else:
            total_threads = 200
    else:
        total_threads = manual_threads
    total_threads = min(total_threads, MAX_LIMIT)
    threads_per_file = total_threads // total_files
    return max(threads_per_file, 2)

# ---------- تشفير بسيط ----------
class CryptoManager:
    def __init__(self, password: str):
        self.password = password
        self.cipher = None
        if CRYPTO_AVAILABLE and password:
            salt = b'kso_salt_2026'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            self.cipher = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, data: str) -> str:
        if self.cipher:
            return self.cipher.encrypt(data.encode()).decode()
        return data

    def decrypt(self, data: str) -> str:
        if self.cipher:
            try:
                return self.cipher.decrypt(data.encode()).decode()
            except:
                return data
        return data

# ---------- Download item ----------
class DownloadItem:
    def __init__(self, url, title, path, quality):
        self.url = url
        self.title = title
        self.path = path
        self.quality = quality
        self.size = 0
        self.downloaded = 0
        self.speed = 0
        self.eta = 0
        self.status = "Pending"
        self.paused = False
        self.cancelled = False
        self.finished = False
        self.row = -1
        self.compressed = False
        self.md5 = ""

# ---------- Download Manager ----------
class DownloadManager(QObject):
    progress_updated = pyqtSignal(int, int, int, int, str)
    finished_signal = pyqtSignal(int)
    error_signal = pyqtSignal(int, str)
    row_added = pyqtSignal(int, str)
    compress_started = pyqtSignal(int)
    compress_finished = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: List[DownloadItem] = []
        self.threads = []
        self.speed_limit = 0
        self.proxy = None
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.use_aria2 = self._check_aria2()
        self.compress_queue = queue.Queue()
        self.compress_thread_running = False
        self.auto_compress_enabled = True
        self.smart_mode = True
        self.manual_threads = 32
        self.compress_mode = "balanced"
        self.delete_original = True
        self.no_duplicate = True
        self.organize_by_type = False

    def _check_aria2(self):
        try:
            subprocess.run(['aria2c', '--version'], capture_output=True, timeout=1)
            return True
        except:
            return False

    def set_proxy(self, proxy_url):
        self.proxy = proxy_url if proxy_url else None

    def set_user_agent(self, ua):
        self.user_agent = ua

    def add_download(self, url, path, quality, title=None):
        # منع التكرار
        if self.no_duplicate:
            for item in self.items:
                if item.url == url and not item.finished:
                    notification.notify(title="KSO", message="الرابط موجود بالفعل", timeout=3)
                    return -1
        item = DownloadItem(url, title or os.path.basename(url), path, quality)
        self.items.append(item)
        row = len(self.items) - 1
        item.row = row
        self.row_added.emit(row, item.title)
        self.start_download(row)
        return row

    def start_download(self, row):
        item = self.items[row]
        if item.finished or item.cancelled:
            return
        if item.status == "Downloading":
            return
        if item.status == "Paused":
            self.resume_download(row)
            return

        total_files = len(self.items)
        threads = get_smart_threads(total_files, self.smart_mode, self.manual_threads)

        def run():
            try:
                quality = item.quality
                format_sel = 'bestvideo+bestaudio' if 'MP3' not in quality else 'bestaudio'
                if "MP3" in quality:
                    format_sel = 'bestaudio'
                ydl_opts = {
                    'outtmpl': os.path.join(item.path, '%(title)s.%(ext)s'),
                    'fragment_retries': 10,
                    'merge_output_format': 'mp4',
                    'format': format_sel,
                    'nocheckcertificate': True,
                    'noplaylist': False,
                    'progress_hooks': [self._progress_hook(row)],
                    'quiet': True,
                    'no_warnings': True,
                    'throttled_rate': self.speed_limit * 1024 if self.speed_limit > 0 else None,
                    'user_agent': self.user_agent,
                }
                if ydl_opts['throttled_rate'] is None:
                    del ydl_opts['throttled_rate']

                if self.proxy:
                    ydl_opts['proxy'] = self.proxy

                if self.use_aria2:
                    ydl_opts['external_downloader'] = 'aria2c'
                    ydl_opts['external_downloader_args'] = ['-j', str(threads), '-x', '16', '-s', str(threads), '-k', '1M']
                else:
                    ydl_opts['concurrent_fragments'] = threads

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.items[row].status = "Downloading"
                    self.progress_updated.emit(row, 0, 0, 0, "Downloading")
                    ydl.download([item.url])
            except Exception as e:
                self.items[row].status = "Error"
                self.error_signal.emit(row, str(e))
                self.progress_updated.emit(row, 0, 0, 0, "Error")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.threads.append(thread)

    def _progress_hook(self, row):
        def hook(d):
            item = self.items[row]
            if item.cancelled:
                return
            if d['status'] == 'downloading':
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                self.items[row].size = total
                self.items[row].downloaded = downloaded
                self.items[row].speed = speed
                self.items[row].eta = eta
                status = "Paused" if item.paused else "Downloading"
                self.progress_updated.emit(row, downloaded, total, speed, status)
            elif d['status'] == 'finished':
                self.items[row].finished = True
                self.items[row].status = "Finished"
                # حساب MD5 للملف
                out_file = d.get('filename', '')
                if out_file and os.path.exists(out_file):
                    try:
                        with open(out_file, 'rb') as f:
                            self.items[row].md5 = hashlib.md5(f.read()).hexdigest()
                    except:
                        pass
                self.progress_updated.emit(row, d.get('total_bytes', 0), d.get('total_bytes', 0), 0, "Finished")
                self.finished_signal.emit(row)
                notification.notify(title="KSO", message=f"تم الانتهاء: {item.title}", timeout=5)
                self._add_to_compress_queue(row)
        return hook

    def _add_to_compress_queue(self, row):
        if self.auto_compress_enabled:
            self.compress_queue.put(row)
            self._start_compress_worker()

    def _start_compress_worker(self):
        if not self.compress_thread_running:
            self.compress_thread_running = True
            thread = threading.Thread(target=self._compress_worker, daemon=True)
            thread.start()

    def _compress_worker(self):
        settings = {
            "fast": {"crf": 23, "preset": "ultrafast"},
            "balanced": {"crf": 28, "preset": "fast"},
            "max": {"crf": 32, "preset": "slow"}
        }
        while True:
            try:
                row = self.compress_queue.get(timeout=1)
            except queue.Empty:
                self.compress_thread_running = False
                break
            self._do_auto_compress(row, settings)
            self.compress_queue.task_done()

    def _do_auto_compress(self, row, settings):
        item = self.items[row]
        if not item or not item.finished or item.compressed:
            return

        base = os.path.join(item.path, item.title)
        input_file = None
        for ext in [".mp4", ".mkv", ".webm", ".avi", ".mov"]:
            test = base + ext
            if os.path.exists(test):
                input_file = test
                break
        if not input_file:
            self.compress_finished.emit(row, False)
            return

        output_file = input_file.replace(os.path.splitext(input_file)[1], "_KSO_Auto.mp4")
        if not self._check_ffmpeg():
            notification.notify(title="KSO", message=self._get_lang("auto_compress_stopped"), timeout=5)
            self.compress_finished.emit(row, False)
            return

        self.items[row].status = "Compressing"
        self.progress_updated.emit(row, item.size, item.size, 0, "Compressing")
        self.compress_started.emit(row)

        mode = self.compress_mode
        s = settings.get(mode, settings["balanced"])
        cmd = ["ffmpeg", "-i", input_file, "-vcodec", "libx265", "-crf", str(s["crf"]),
               "-preset", s["preset"], "-acodec", "aac", "-b:a", "128k", "-threads", "0", "-y", output_file]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.items[row].compressed = True
            self.items[row].status = "Compressed"
            self.progress_updated.emit(row, item.size, item.size, 0, "Compressed")
            self.compress_finished.emit(row, True)
            notification.notify(title="KSO", message=f"تم ضغط: {item.title}", timeout=5)

            if self.delete_original:
                try:
                    os.remove(input_file)
                    notification.notify(title="KSO", message=self._get_lang("file_deleted"), timeout=3)
                except:
                    pass
        except subprocess.CalledProcessError as e:
            self.items[row].status = "Error"
            self.error_signal.emit(row, f"فشل الضغط التلقائي: {e.stderr.decode()}")
            self.compress_finished.emit(row, False)
            notification.notify(title="KSO", message=self._get_lang("auto_compress_failed"), timeout=5)

    def _check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=1)
            return True
        except:
            return False

    def _get_lang(self, key):
        if hasattr(self.parent(), 'lang'):
            return self.parent().lang.get(key, key)
        return key

    def pause_download(self, row):
        item = self.items[row]
        if item.status == "Downloading":
            item.paused = True
            item.status = "Paused"
            self.progress_updated.emit(row, item.downloaded, item.size, 0, "Paused")

    def resume_download(self, row):
        item = self.items[row]
        if item.status == "Paused" and not item.finished:
            item.paused = False
            self.start_download(row)

    def delete_download(self, row):
        item = self.items[row]
        item.cancelled = True
        item.finished = True
        self.items[row] = None

    def get_item(self, row):
        if 0 <= row < len(self.items):
            return self.items[row]
        return None

    def set_speed_limit(self, limit_kb):
        self.speed_limit = limit_kb

    def set_auto_compress(self, enabled):
        self.auto_compress_enabled = enabled

    def set_smart_mode(self, enabled):
        self.smart_mode = enabled

    def set_manual_threads(self, threads):
        self.manual_threads = threads

    def set_compress_mode(self, mode):
        self.compress_mode = mode

    def set_delete_original(self, delete):
        self.delete_original = delete

    def set_no_duplicate(self, enabled):
        self.no_duplicate = enabled

# ---------- Main Application ----------
class KSOApp(QMainWindow):
    def __init__(self, cli_mode=False):
        self.cli_mode = cli_mode
        self.ffmpeg_available = self._check_ffmpeg()
        super().__init__()
        self.lang_code = "ar"
        self.lang = self.load_lang(self.lang_code)
        self.config = self.load_config()
        self.password = self.config.get("password", "")
        self.crypto = CryptoManager(self.password)

        if self.password:
            pwd, ok = QInputDialog.getText(self, self.lang["title"], self.lang["enter_password"], QLineEdit.EchoMode.Password)
            if not ok or pwd != self.password:
                QMessageBox.critical(self, "Error", self.lang["wrong_password"])
                sys.exit(0)

        self.setWindowTitle(self.lang["title"])
        self.resize(1500, 950)
        self.setWindowIcon(self.load_icon())
        self.setAcceptDrops(True)  # لتفعيل السحب والإفلات

        self.download_manager = DownloadManager()
        self.download_manager.parent = self
        self.download_manager.progress_updated.connect(self.update_download_row)
        self.download_manager.finished_signal.connect(self.on_download_finished)
        self.download_manager.error_signal.connect(self.on_download_error)
        self.download_manager.row_added.connect(self.add_table_row)
        self.download_manager.compress_started.connect(self.on_compress_started)
        self.download_manager.compress_finished.connect(self.on_compress_finished)

        self.history = self.load_history()
        self.init_ui()
        self.init_hotkeys()
        self.update_yt_dlp()
        self.apply_theme()
        self.setup_schedule_checker()
        self.setup_resource_monitor()
        self.load_settings()

        if not self.config.get("welcome_shown", False):
            self.show_welcome()

    # ---------- دعم السحب والإفلات ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            link = url.toString()
            if link.startswith("http"):
                self.start_download(link)

    def _check_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=1)
            return True
        except:
            return False

    def load_lang(self, code):
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if code in data:
                    return data[code]
        return DEFAULT_LANG.get(code, DEFAULT_LANG["ar"])

    def save_lang(self, code):
        data = {}
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        data[code] = self.lang
        with open(LANG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if CRYPTO_AVAILABLE and data.get("encrypted"):
                    try:
                        crypto = CryptoManager(data.get("password", ""))
                        for key in ["history", "downloads"]:
                            if key in data and isinstance(data[key], str):
                                data[key] = json.loads(crypto.decrypt(data[key]))
                    except:
                        pass
                return data
        return {
            "path": os.path.expanduser("~/Downloads"),
            "quality": "1080p",
            "parallel": 4,
            "shutdown": False,
            "password": "",
            "speed_limit": 0,
            "schedule_time": "00:00",
            "auto_compress": True,
            "smart_mode": True,
            "manual_threads": 32,
            "proxy": "",
            "compress_mode": "balanced",
            "delete_original": True,
            "no_duplicate": True,
            "welcome_shown": False,
            "encrypted": False
        }

    def save_config(self):
        data = self.config.copy()
        if CRYPTO_AVAILABLE and self.password:
            crypto = CryptoManager(self.password)
            for key in ["history", "downloads"]:
                if key in data and isinstance(data[key], list):
                    data[key] = crypto.encrypt(json.dumps(data[key]))
            data["encrypted"] = True
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_history(self, entry):
        self.history.append(entry)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_icon(self):
        icon_path = "app_icon.ico"
        if not os.path.exists(icon_path):
            self.generate_icon()
        return QIcon(icon_path)

    def generate_icon(self):
        try:
            from PIL import Image, ImageDraw, ImageFont
            size = 256
            img = Image.new('RGBA', (size, size), (0, 120, 215, 255))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arialbd.ttf", 90)
            except:
                font = ImageFont.load_default()
            draw.text((size//2-70, size//2-60), "KSO", fill="white", font=font)
            draw.polygon([(size//2+40, size//2+10), (size//2+70, size//2+40), (size//2+10, size//2+40)], fill="white")
            img.save("app_icon.ico")
        except:
            pass

    def show_welcome(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.lang.get("welcome", "Welcome"))
        dlg.resize(500, 300)
        layout = QVBoxLayout(dlg)
        label = QLabel(self.lang.get("welcome_text", "Welcome text"))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn = QPushButton("OK")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.exec()
        self.config["welcome_shown"] = True
        self.save_config()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Watermark
        self.watermark = QLabel("KSO", self)
        self.watermark.setStyleSheet("font-size: 180px; color: rgba(100,100,100,20); font-weight: 900;")
        self.watermark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.watermark.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.watermark.setGeometry(0, 0, self.width(), self.height())
        self.watermark.lower()

        self.create_toolbar()

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Browser
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://youtube.com"))
        self.browser.urlChanged.connect(self.on_browser_url_changed)
        self.browser.page().profile().downloadRequested.connect(self.handle_download)
        # حظر الإعلانات البسيط
        self.browser.page().profile().setRequestInterceptor(self._ad_blocker)
        splitter.addWidget(self.browser)

        # Tabs: Search + Study
        self.tabs = QTabWidget()
        self.search_tab = self.create_search_tab()
        self.study_tab = self.create_study_tab()
        self.tabs.addTab(self.search_tab, self.lang.get("search", "Search"))
        self.tabs.addTab(self.study_tab, self.lang.get("study", "Study"))
        splitter.addWidget(self.tabs)

        # Download table
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(8)
        self.downloads_table.setHorizontalHeaderLabels([
            self.lang["name"], self.lang["progress"], self.lang["speed_dl"],
            self.lang["size"], self.lang["remaining"], self.lang["status"],
            self.lang["pause"], self.lang["delete"]
        ])
        self.downloads_table.horizontalHeader().setStretchLastSection(True)
        self.downloads_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.downloads_table.customContextMenuRequested.connect(self.show_context_menu)
        splitter.addWidget(self.downloads_table)

        # Filter and history bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(self.lang.get("filter", "Filter:")))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([self.lang.get("filter_all", "All"),
                                    self.lang.get("filter_finished", "Finished"),
                                    self.lang.get("filter_downloading", "Downloading"),
                                    self.lang.get("filter_error", "Error")])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText(self.lang.get("history_search", "Search history..."))
        self.history_search.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.history_search)

        self.re_download_btn = QPushButton(self.lang.get("re_download", "Re-download"))
        self.re_download_btn.clicked.connect(self.re_download_selected)
        filter_layout.addWidget(self.re_download_btn)

        self.export_csv_btn = QPushButton(self.lang.get("export_csv", "Export CSV"))
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        filter_layout.addWidget(self.export_csv_btn)

        self.backup_btn = QPushButton(self.lang.get("backup", "Backup"))
        self.backup_btn.clicked.connect(self.backup_settings)
        filter_layout.addWidget(self.backup_btn)

        self.restore_btn = QPushButton(self.lang.get("restore", "Restore"))
        self.restore_btn.clicked.connect(self.restore_settings)
        filter_layout.addWidget(self.restore_btn)

        self.clear_cache_btn = QPushButton(self.lang.get("clear_cache", "Clear Cache"))
        self.clear_cache_btn.clicked.connect(self.clear_browser_cache)
        filter_layout.addWidget(self.clear_cache_btn)

        self.clear_temp_btn = QPushButton(self.lang.get("clear_temp", "Clear Temp"))
        self.clear_temp_btn.clicked.connect(self.clear_temp_files)
        filter_layout.addWidget(self.clear_temp_btn)

        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addLayout(filter_layout)
        table_layout.addWidget(self.downloads_table)
        splitter.addWidget(table_widget)

        main_layout.addWidget(splitter)
        splitter.setSizes([400, 200, 300])

        # Status bar with resource monitor
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.resource_label = QLabel("")
        self.status_bar.addPermanentWidget(self.resource_label)
        self.status_bar.showMessage(self.lang.get("drag_drop", "Drag & Drop link here"))

        self.downloads_table.cellClicked.connect(self.on_table_cell_clicked)

    def _ad_blocker(self, request):
        # حظر إعلانات بسيط
        url = request.url().toString()
        if any(ad in url for ad in ["doubleclick", "googleads", "googlesyndication"]):
            request.setBlocked(True)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.lang_btn = QPushButton("🇸🇦 عربي")
        self.lang_btn.clicked.connect(self.toggle_language)
        toolbar.addWidget(self.lang_btn)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel(self.lang["quality"]))
        self.quality_box = QComboBox()
        self.quality_box.addItems(["8K", "4K", "1080p", "720p", "480p", "MP3 320"])
        self.quality_box.setCurrentText(self.config.get("quality", "1080p"))
        toolbar.addWidget(self.quality_box)

        toolbar.addWidget(QLabel(self.lang["path"]))
        self.path_btn = QPushButton(self.config.get("path", os.path.expanduser("~/Downloads")))
        self.path_btn.clicked.connect(self.browse_path)
        toolbar.addWidget(self.path_btn)

        toolbar.addWidget(QLabel(self.lang["count"]))
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setRange(1, 16)
        self.parallel_spin.setValue(self.config.get("parallel", 4))
        toolbar.addWidget(self.parallel_spin)

        self.smart_mode_check = QCheckBox(self.lang.get("smart_mode", "Smart"))
        self.smart_mode_check.setChecked(self.config.get("smart_mode", True))
        self.smart_mode_check.stateChanged.connect(self.on_smart_mode_toggle)
        toolbar.addWidget(self.smart_mode_check)

        toolbar.addWidget(QLabel(self.lang.get("manual_threads", "Threads")))
        self.manual_threads_spin = QSpinBox()
        self.manual_threads_spin.setRange(1, MAX_LIMIT)
        self.manual_threads_spin.setValue(self.config.get("manual_threads", 32))
        self.manual_threads_spin.valueChanged.connect(self.on_manual_threads_changed)
        toolbar.addWidget(self.manual_threads_spin)

        toolbar.addWidget(QLabel(self.lang.get("proxy", "Proxy")))
        self.proxy_edit = QLineEdit()
        self.proxy_edit.setPlaceholderText("http://user:pass@host:port")
        self.proxy_edit.setText(self.config.get("proxy", ""))
        self.proxy_edit.textChanged.connect(self.on_proxy_changed)
        toolbar.addWidget(self.proxy_edit)

        self.browser_toggle = QAction(self.lang["browser"], self, checkable=True)
        self.browser_toggle.setChecked(True)
        self.browser_toggle.toggled.connect(self.browser.setVisible)
        toolbar.addAction(self.browser_toggle)

        self.shutdown_check = QCheckBox(self.lang["shutdown"])
        self.shutdown_check.setChecked(self.config.get("shutdown", False))
        toolbar.addWidget(self.shutdown_check)

        toolbar.addWidget(QLabel(self.lang["schedule"]))
        self.schedule_edit = QTimeEdit()
        self.schedule_edit.setDisplayFormat("HH:mm")
        self.schedule_edit.setTime(QTime.currentTime())
        if "schedule_time" in self.config:
            self.schedule_edit.setTime(QTime.fromString(self.config["schedule_time"], "HH:mm"))
        toolbar.addWidget(self.schedule_edit)

        toolbar.addWidget(QLabel(self.lang["speed_limit"]))
        self.speed_limit_spin = QSpinBox()
        self.speed_limit_spin.setRange(0, 999999)
        self.speed_limit_spin.setSuffix(" KB/s")
        self.speed_limit_spin.setValue(self.config.get("speed_limit", 0))
        self.speed_limit_spin.valueChanged.connect(self.on_speed_limit_changed)
        toolbar.addWidget(self.speed_limit_spin)

        toolbar.addWidget(QLabel(self.lang["password"]))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setText(self.config.get("password", ""))
        self.password_edit.setPlaceholderText("كلمة السر")
        toolbar.addWidget(self.password_edit)

        self.auto_compress_check = QCheckBox(self.lang.get("auto_compress", "AutoComp"))
        self.auto_compress_check.setChecked(self.config.get("auto_compress", True))
        self.auto_compress_check.stateChanged.connect(self.on_auto_compress_toggle)
        toolbar.addWidget(self.auto_compress_check)

        toolbar.addWidget(QLabel(self.lang.get("compress_mode", "Mode")))
        self.compress_mode_combo = QComboBox()
        self.compress_mode_combo.addItems([self.lang.get("mode_fast", "Fast"),
                                           self.lang.get("mode_balanced", "Balanced"),
                                           self.lang.get("mode_max", "Max")])
        self.compress_mode_combo.setCurrentText(self.config.get("compress_mode", "Balanced"))
        self.compress_mode_combo.currentTextChanged.connect(self.on_compress_mode_changed)
        toolbar.addWidget(self.compress_mode_combo)

        self.delete_original_check = QCheckBox(self.lang.get("delete_original", "DelOrig"))
        self.delete_original_check.setChecked(self.config.get("delete_original", True))
        self.delete_original_check.stateChanged.connect(self.on_delete_original_toggle)
        toolbar.addWidget(self.delete_original_check)

        self.no_duplicate_check = QCheckBox(self.lang.get("no_duplicate", "NoDup"))
        self.no_duplicate_check.setChecked(self.config.get("no_duplicate", True))
        self.no_duplicate_check.stateChanged.connect(self.on_no_duplicate_toggle)
        toolbar.addWidget(self.no_duplicate_check)

        # أزرار إضافية
        self.preview_btn = QAction(self.lang.get("preview", "Preview"), self)
        self.preview_btn.triggered.connect(self.open_preview)
        toolbar.addAction(self.preview_btn)

        self.download_page_btn = QAction(self.lang.get("download_page", "Download Page"), self)
        self.download_page_btn.triggered.connect(self.download_current_page)
        toolbar.addAction(self.download_page_btn)

        about_btn = QAction(self.lang["about"], self)
        about_btn.triggered.connect(self.show_about)
        toolbar.addAction(about_btn)

        self.on_smart_mode_toggle(self.smart_mode_check.isChecked())

    def load_settings(self):
        self.download_manager.set_smart_mode(self.smart_mode_check.isChecked())
        self.download_manager.set_manual_threads(self.manual_threads_spin.value())
        self.download_manager.set_auto_compress(self.auto_compress_check.isChecked())
        self.download_manager.set_speed_limit(self.speed_limit_spin.value())
        self.download_manager.set_proxy(self.proxy_edit.text().strip())
        mode = self.compress_mode_combo.currentText()
        mode_map = {"Fast": "fast", "Balanced": "balanced", "Max": "max"}
        self.download_manager.set_compress_mode(mode_map.get(mode, "balanced"))
        self.download_manager.set_delete_original(self.delete_original_check.isChecked())
        self.download_manager.set_no_duplicate(self.no_duplicate_check.isChecked())

    def on_proxy_changed(self, text):
        self.download_manager.set_proxy(text.strip())
        self.config["proxy"] = text.strip()
        self.save_config()

    def on_compress_mode_changed(self, text):
        mode_map = {"Fast": "fast", "Balanced": "balanced", "Max": "max"}
        self.download_manager.set_compress_mode(mode_map.get(text, "balanced"))
        self.config["compress_mode"] = text
        self.save_config()

    def on_delete_original_toggle(self, state):
        enabled = state == Qt.CheckState.Checked
        self.download_manager.set_delete_original(enabled)
        self.config["delete_original"] = enabled
        self.save_config()

    def on_no_duplicate_toggle(self, state):
        enabled = state == Qt.CheckState.Checked
        self.download_manager.set_no_duplicate(enabled)
        self.config["no_duplicate"] = enabled
        self.save_config()

    def on_smart_mode_toggle(self, state):
        enabled = state == Qt.CheckState.Checked if isinstance(state, int) else state
        self.manual_threads_spin.setEnabled(not enabled)
        self.download_manager.set_smart_mode(enabled)
        self.config["smart_mode"] = enabled
        self.save_config()

    def on_manual_threads_changed(self, value):
        self.download_manager.set_manual_threads(value)
        self.config["manual_threads"] = value
        self.save_config()

    def on_auto_compress_toggle(self, state):
        enabled = state == Qt.CheckState.Checked
        self.download_manager.set_auto_compress(enabled)
        self.config["auto_compress"] = enabled
        self.save_config()

    def on_speed_limit_changed(self, value):
        self.download_manager.set_speed_limit(value)

    def apply_filter(self, filter_text):
        for row in range(self.downloads_table.rowCount()):
            item = self.download_manager.get_item(row)
            if item:
                status = item.status
                show = True
                if filter_text == self.lang.get("filter_finished", "Finished"):
                    show = status in ["Finished", "Compressed"]
                elif filter_text == self.lang.get("filter_downloading", "Downloading"):
                    show = status in ["Downloading", "Compressing", "Pending"]
                elif filter_text == self.lang.get("filter_error", "Error"):
                    show = status == "Error"
                self.downloads_table.setRowHidden(row, not show)

    def clear_browser_cache(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        QMessageBox.information(self, self.lang["title"], "تم مسح الكاش")

    def clear_temp_files(self):
        temp_dir = tempfile.gettempdir()
        try:
            shutil.rmtree(os.path.join(temp_dir, "kso_temp"), ignore_errors=True)
            QMessageBox.information(self, self.lang["title"], "تم تنظيف الملفات المؤقتة")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def backup_settings(self):
        path = QFileDialog.getSaveFileName(self, "حفظ النسخة الاحتياطية", "kso_backup.json", "JSON (*.json)")[0]
        if path:
            shutil.copy(CONFIG_FILE, path)
            QMessageBox.information(self, self.lang["title"], "تم حفظ النسخة الاحتياطية")

    def restore_settings(self):
        path = QFileDialog.getOpenFileName(self, "استعادة النسخة الاحتياطية", "", "JSON (*.json)")[0]
        if path and os.path.exists(path):
            shutil.copy(path, CONFIG_FILE)
            self.config = self.load_config()
            self.load_settings()
            QMessageBox.information(self, self.lang["title"], "تم استعادة الإعدادات")

    def export_to_csv(self):
        path = QFileDialog.getSaveFileName(self, "تصدير CSV", "downloads.csv", "CSV (*.csv)")[0]
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "URL", "Path", "Quality", "Status", "Date", "MD5"])
                    for item in self.history:
                        writer.writerow([item.get("name", ""), item.get("url", ""),
                                         item.get("path", ""), item.get("quality", ""),
                                         item.get("status", ""), item.get("date", ""),
                                         item.get("md5", "")])
                QMessageBox.information(self, self.lang["title"], "تم التصدير بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def setup_resource_monitor(self):
        def update():
            while True:
                if psutil:
                    ram = psutil.virtual_memory()
                    cpu = psutil.cpu_percent()
                    text = self.lang.get("resources", "RAM: {ram} MB | CPU: {cpu}%").format(
                        ram=round(ram.used / 1024 / 1024, 1), cpu=cpu)
                    QMetaObject.invokeMethod(self.resource_label, "setText",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(str, text))
                time.sleep(2)
        threading.Thread(target=update, daemon=True).start()

    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.lang.get("search", "Search YouTube..."))
        self.search_input.returnPressed.connect(self.search_youtube)
        layout.addWidget(self.search_input)

        self.search_result_tabs = QTabWidget()
        self.all_list = QListWidget()
        self.all_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.videos_list = QListWidget()
        self.videos_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.playlists_list = QListWidget()
        self.playlists_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.shorts_list = QListWidget()
        self.shorts_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.all_list.itemDoubleClicked.connect(self.on_search_item_double_clicked)
        self.videos_list.itemDoubleClicked.connect(self.on_search_item_double_clicked)
        self.playlists_list.itemDoubleClicked.connect(self.on_search_item_double_clicked)
        self.shorts_list.itemDoubleClicked.connect(self.on_search_item_double_clicked)

        self.search_result_tabs.addTab(self.all_list, self.lang.get("tab_all", "All"))
        self.search_result_tabs.addTab(self.videos_list, self.lang.get("tab_videos", "Videos"))
        self.search_result_tabs.addTab(self.playlists_list, self.lang.get("tab_playlists", "Playlists"))
        self.search_result_tabs.addTab(self.shorts_list, self.lang.get("tab_shorts", "Shorts"))
        layout.addWidget(self.search_result_tabs)

        btn_layout = QHBoxLayout()
        download_selected_btn = QPushButton(self.lang.get("download_selected", "Download Selected"))
        download_selected_btn.clicked.connect(self.download_selected_from_search_tab)
        download_all_btn = QPushButton(self.lang.get("download_all", "Download All"))
        download_all_btn.clicked.connect(self.download_all_from_search_tab)
        btn_layout.addWidget(download_selected_btn)
        btn_layout.addWidget(download_all_btn)
        layout.addLayout(btn_layout)

        self.load_more_btn = QPushButton(self.lang.get("load_more", "Load More"))
        self.load_more_btn.clicked.connect(self.search_youtube)
        layout.addWidget(self.load_more_btn)

        return tab

    def on_search_item_double_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.start_download(url)

    def download_selected_from_search_tab(self):
        current_tab = self.search_result_tabs.currentWidget()
        if not current_tab:
            return
        selected_items = current_tab.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.lang["title"], "الرجاء اختيار عنصر واحد على الأقل")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for item in selected_items:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        notification.notify(title="KSO", message=f"تم بدء تحميل {len(selected_items)} عنصر", timeout=3)

    def download_all_from_search_tab(self):
        current_tab = self.search_result_tabs.currentWidget()
        if not current_tab:
            return
        count = current_tab.count()
        if count == 0:
            QMessageBox.warning(self, self.lang["title"], "لا توجد عناصر للتحميل")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for i in range(count):
            item = current_tab.item(i)
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        notification.notify(title="KSO", message=f"تم بدء تحميل {count} عنصر", timeout=3)

    def create_study_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.study_search = QLineEdit()
        self.study_search.setPlaceholderText(self.lang.get("search_course", "Search course + subject..."))
        self.study_search.returnPressed.connect(self.search_study)
        layout.addWidget(self.study_search)

        self.study_result_tabs = QTabWidget()
        self.study_all_list = QListWidget()
        self.study_all_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.study_videos_list = QListWidget()
        self.study_videos_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.study_playlists_list = QListWidget()
        self.study_playlists_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.study_shorts_list = QListWidget()
        self.study_shorts_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.study_all_list.itemDoubleClicked.connect(self.on_study_item_double_clicked)
        self.study_videos_list.itemDoubleClicked.connect(self.on_study_item_double_clicked)
        self.study_playlists_list.itemDoubleClicked.connect(self.on_study_item_double_clicked)
        self.study_shorts_list.itemDoubleClicked.connect(self.on_study_item_double_clicked)

        self.study_result_tabs.addTab(self.study_all_list, self.lang.get("tab_all", "All"))
        self.study_result_tabs.addTab(self.study_videos_list, self.lang.get("tab_videos", "Videos"))
        self.study_result_tabs.addTab(self.study_playlists_list, self.lang.get("tab_playlists", "Playlists"))
        self.study_result_tabs.addTab(self.study_shorts_list, self.lang.get("tab_shorts", "Shorts"))
        layout.addWidget(self.study_result_tabs)

        btn_layout = QHBoxLayout()
        download_selected_btn = QPushButton(self.lang.get("download_selected", "Download Selected"))
        download_selected_btn.clicked.connect(self.download_selected_from_study_tab)
        download_all_btn = QPushButton(self.lang.get("download_all", "Download All"))
        download_all_btn.clicked.connect(self.download_all_from_study_tab)
        btn_layout.addWidget(download_selected_btn)
        btn_layout.addWidget(download_all_btn)
        layout.addLayout(btn_layout)

        folder_layout = QHBoxLayout()
        self.create_folder_btn = QPushButton(self.lang.get("create_folder", "Create Folder"))
        self.create_folder_btn.clicked.connect(self.create_study_folder)
        self.download_playlist_btn = QPushButton(self.lang.get("download_playlist", "Download Full Playlist"))
        self.download_playlist_btn.clicked.connect(self.download_study_playlist)
        folder_layout.addWidget(self.create_folder_btn)
        folder_layout.addWidget(self.download_playlist_btn)
        layout.addLayout(folder_layout)

        return tab

    def on_study_item_double_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.start_download(url)

    def download_selected_from_study_tab(self):
        current_tab = self.study_result_tabs.currentWidget()
        if not current_tab:
            return
        selected_items = current_tab.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.lang["title"], "الرجاء اختيار عنصر واحد على الأقل")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for item in selected_items:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        notification.notify(title="KSO", message=f"تم بدء تحميل {len(selected_items)} عنصر", timeout=3)

    def download_all_from_study_tab(self):
        current_tab = self.study_result_tabs.currentWidget()
        if not current_tab:
            return
        count = current_tab.count()
        if count == 0:
            QMessageBox.warning(self, self.lang["title"], "لا توجد عناصر للتحميل")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for i in range(count):
            item = current_tab.item(i)
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        notification.notify(title="KSO", message=f"تم بدء تحميل {count} عنصر", timeout=3)

    def toggle_language(self):
        if self.lang_code == "ar":
            self.lang_code = "en"
            self.lang_btn.setText("🇬🇧 English")
        else:
            self.lang_code = "ar"
            self.lang_btn.setText("🇸🇦 عربي")
        self.lang = self.load_lang(self.lang_code)
        self.save_lang(self.lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.lang["title"])
        self.downloads_table.setHorizontalHeaderLabels([
            self.lang["name"], self.lang["progress"], self.lang["speed_dl"],
            self.lang["size"], self.lang["remaining"], self.lang["status"],
            self.lang["pause"], self.lang["delete"]
        ])
        self.search_input.setPlaceholderText(self.lang.get("search", "Search YouTube..."))
        self.load_more_btn.setText(self.lang.get("load_more", "Load More"))
        self.search_result_tabs.setTabText(0, self.lang.get("tab_all", "All"))
        self.search_result_tabs.setTabText(1, self.lang.get("tab_videos", "Videos"))
        self.search_result_tabs.setTabText(2, self.lang.get("tab_playlists", "Playlists"))
        self.search_result_tabs.setTabText(3, self.lang.get("tab_shorts", "Shorts"))

        self.study_result_tabs.setTabText(0, self.lang.get("tab_all", "All"))
        self.study_result_tabs.setTabText(1, self.lang.get("tab_videos", "Videos"))
        self.study_result_tabs.setTabText(2, self.lang.get("tab_playlists", "Playlists"))
        self.study_result_tabs.setTabText(3, self.lang.get("tab_shorts", "Shorts"))

        self.study_search.setPlaceholderText(self.lang.get("search_course", "Search course + subject..."))
        self.create_folder_btn.setText(self.lang.get("create_folder", "Create Folder"))
        self.download_playlist_btn.setText(self.lang.get("download_playlist", "Download Full Playlist"))
        self.history_search.setPlaceholderText(self.lang.get("history_search", "Search history..."))
        self.re_download_btn.setText(self.lang.get("re_download", "Re-download"))
        self.shutdown_check.setText(self.lang["shutdown"])
        self.browser_toggle.setText(self.lang["browser"])
        self.auto_compress_check.setText(self.lang.get("auto_compress", "AutoComp"))
        self.smart_mode_check.setText(self.lang.get("smart_mode", "Smart"))
        self.export_csv_btn.setText(self.lang.get("export_csv", "Export CSV"))
        self.backup_btn.setText(self.lang.get("backup", "Backup"))
        self.restore_btn.setText(self.lang.get("restore", "Restore"))
        self.clear_cache_btn.setText(self.lang.get("clear_cache", "Clear Cache"))
        self.clear_temp_btn.setText(self.lang.get("clear_temp", "Clear Temp"))
        self.no_duplicate_check.setText(self.lang.get("no_duplicate", "NoDup"))
        self.delete_original_check.setText(self.lang.get("delete_original", "DelOrig"))
        self.preview_btn.setText(self.lang.get("preview", "Preview"))
        self.download_page_btn.setText(self.lang.get("download_page", "Download Page"))
        self.status_bar.showMessage(self.lang.get("drag_drop", "Drag & Drop link here"))

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, self.lang["path"])
        if path:
            self.path_btn.setText(path)
            self.config["path"] = path
            self.save_config()

    def setup_schedule_checker(self):
        def check_schedule():
            while True:
                now = QTime.currentTime().toString("HH:mm")
                scheduled = self.schedule_edit.time().toString("HH:mm")
                if now == scheduled:
                    self.start_all_pending()
                    time.sleep(60)
                time.sleep(10)
        threading.Thread(target=check_schedule, daemon=True).start()

    def start_all_pending(self):
        for i in range(len(self.download_manager.items)):
            item = self.download_manager.get_item(i)
            if item and item.status == "Pending":
                self.download_manager.start_download(i)

    def handle_download(self, item: QWebEngineDownloadRequest):
        url = item.url().toString()
        if any(ext in url.lower() for ext in [".exe", ".pdf", ".zip", ".mp4", ".mkv", ".m3u8"]):
            self.start_download(url)
        item.cancel()

    def on_browser_url_changed(self, url):
        if "youtube.com/watch" in url.toString() or "youtu.be/" in url.toString():
            reply = QMessageBox.question(self, self.lang["title"], self.lang.get("auto_capture", "Video found. Add to downloads?"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.start_download(url.toString())

    def open_preview(self):
        # مشغل فيديو بسيط لمعاينة الرابط المحدد
        url = QInputDialog.getText(self, "Preview", "Enter video URL:")[0]
        if url and url.startswith("http"):
            player = QMediaPlayer()
            audio = QAudioOutput()
            player.setAudioOutput(audio)
            player.setSource(QUrl(url))
            player.play()
            # نعرض نافذة صغيرة
            preview_dlg = QDialog(self)
            preview_dlg.setWindowTitle("Preview")
            preview_dlg.resize(640, 480)
            layout = QVBoxLayout(preview_dlg)
            layout.addWidget(QMediaPlayer(player))
            preview_dlg.exec()

    def download_current_page(self):
        # تحميل الصفحة الحالية باستخدام wget (يتطلب تثبيت wget)
        url = self.browser.url().toString()
        if url:
            path = QFileDialog.getExistingDirectory(self, "Save page to")
            if path:
                threading.Thread(target=self._download_page, args=(url, path), daemon=True).start()

    def _download_page(self, url, path):
        try:
            subprocess.run(["wget", "-r", "-p", "-k", "--no-parent", url], cwd=path, check=True)
            QMetaObject.invokeMethod(self, "show_conversion_success", Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(str, "تم تحميل الصفحة بنجاح"))
        except:
            QMetaObject.invokeMethod(self, "show_conversion_error", Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(str, "فشل تحميل الصفحة (تأكد من تثبيت wget)"))

    def show_playlist_items(self, url):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.lang.get("playlist_title", "Select Playlist Videos"))
        dialog.resize(600, 500)

        layout = QVBoxLayout(dialog)
        loading_label = QLabel(self.lang.get("loading_playlist", "Loading playlist..."))
        layout.addWidget(loading_label)

        self.playlist_items_list = QListWidget()
        self.playlist_items_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.playlist_items_list)

        btn_layout = QHBoxLayout()
        download_selected_btn = QPushButton(self.lang.get("download_selected", "Download Selected"))
        download_selected_btn.clicked.connect(lambda: self.download_selected_from_playlist(dialog))
        download_all_btn = QPushButton(self.lang.get("download_all", "Download All"))
        download_all_btn.clicked.connect(lambda: self.download_all_from_playlist(url, dialog))
        btn_layout.addWidget(download_selected_btn)
        btn_layout.addWidget(download_all_btn)
        layout.addLayout(btn_layout)

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        def fetch_playlist():
            try:
                ydl_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True
                }
                if self.download_manager.proxy:
                    ydl_opts['proxy'] = self.download_manager.proxy
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if 'entries' in info:
                        entries = info['entries']
                        for entry in entries:
                            video_title = entry.get('title', 'Unknown')
                            video_id = entry.get('id', '')
                            item = QListWidgetItem(video_title)
                            video_url = f"https://youtube.com/watch?v={video_id}"
                            item.setData(Qt.ItemDataRole.UserRole, video_url)
                            QMetaObject.invokeMethod(self.playlist_items_list, "addItem",
                                                     Qt.ConnectionType.QueuedConnection,
                                                     Q_ARG(QListWidgetItem, item))
                    else:
                        video_title = info.get('title', 'Unknown')
                        video_url = info.get('webpage_url', url)
                        item = QListWidgetItem(video_title)
                        item.setData(Qt.ItemDataRole.UserRole, video_url)
                        QMetaObject.invokeMethod(self.playlist_items_list, "addItem",
                                                 Qt.ConnectionType.QueuedConnection,
                                                 Q_ARG(QListWidgetItem, item))
                    QMetaObject.invokeMethod(loading_label, "setText",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(str, f"عدد الفيديوهات: {self.playlist_items_list.count()}"))
            except Exception as e:
                QMetaObject.invokeMethod(self, "show_error",
                                         Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(str, f"فشل تحميل البلاي ليست: {e}"))

        threading.Thread(target=fetch_playlist, daemon=True).start()
        dialog.exec()

    def download_selected_from_playlist(self, dialog):
        selected_items = self.playlist_items_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.lang["title"], "الرجاء اختيار فيديو واحد على الأقل")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for item in selected_items:
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        dialog.accept()
        notification.notify(title="KSO", message=f"تم بدء تحميل {len(selected_items)} فيديو", timeout=3)

    def download_all_from_playlist(self, url, dialog):
        count = self.playlist_items_list.count()
        if count == 0:
            QMessageBox.warning(self, self.lang["title"], "لا توجد فيديوهات")
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        for i in range(count):
            item = self.playlist_items_list.item(i)
            url = item.data(Qt.ItemDataRole.UserRole)
            if url:
                self.download_manager.add_download(url, path, quality)
        dialog.accept()
        notification.notify(title="KSO", message=f"تم بدء تحميل {count} فيديو", timeout=3)

    def start_download(self, url):
        if 'playlist' in url.lower() or 'list=' in url.lower():
            self.show_playlist_items(url)
            return
        quality = self.quality_box.currentText()
        path = self.config["path"]
        row = self.download_manager.add_download(url, path, quality)
        if row != -1:
            notification.notify(title="KSO", message="بدأ التحميل", timeout=3)

    def add_table_row(self, row, title):
        self.downloads_table.insertRow(row)
        self.downloads_table.setItem(row, 0, QTableWidgetItem(title or "Unknown"))
        self.downloads_table.setItem(row, 1, QTableWidgetItem("0%"))
        self.downloads_table.setItem(row, 2, QTableWidgetItem("0 KB/s"))
        self.downloads_table.setItem(row, 3, QTableWidgetItem("0 MB"))
        self.downloads_table.setItem(row, 4, QTableWidgetItem("--"))
        self.downloads_table.setItem(row, 5, QTableWidgetItem(self.lang.get("pending", "Pending")))
        pause_btn = QPushButton(self.lang.get("pause", "Pause"))
        pause_btn.setProperty("row", row)
        pause_btn.clicked.connect(lambda checked, r=row: self.pause_download(r))
        self.downloads_table.setCellWidget(row, 6, pause_btn)
        del_btn = QPushButton(self.lang.get("delete", "Delete"))
        del_btn.setProperty("row", row)
        del_btn.clicked.connect(lambda checked, r=row: self.delete_download(r))
        self.downloads_table.setCellWidget(row, 7, del_btn)
        self.apply_filter(self.filter_combo.currentText())

    def update_download_row(self, row, downloaded, total, speed, status):
        if row >= self.downloads_table.rowCount():
            return
        item = self.download_manager.get_item(row)
        if not item:
            return
        if total > 0:
            progress = int((downloaded / total) * 100)
        else:
            progress = 0
        self.downloads_table.setItem(row, 1, QTableWidgetItem(f"{progress}%"))
        speed_text = f"{speed/1024:.1f} KB/s" if speed else "0 KB/s"
        self.downloads_table.setItem(row, 2, QTableWidgetItem(speed_text))
        size_mb = total / 1024 / 1024
        self.downloads_table.setItem(row, 3, QTableWidgetItem(f"{size_mb:.2f} MB"))
        if speed > 0 and total > downloaded:
            eta_sec = (total - downloaded) / speed
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_sec))
        else:
            eta_str = "--"
        self.downloads_table.setItem(row, 4, QTableWidgetItem(eta_str))
        status_text = self.lang.get(status.lower(), status)
        self.downloads_table.setItem(row, 5, QTableWidgetItem(status_text))
        pause_btn = self.downloads_table.cellWidget(row, 6)
        if pause_btn:
            if status == "Paused":
                pause_btn.setText(self.lang.get("resume", "Resume"))
            else:
                pause_btn.setText(self.lang.get("pause", "Pause"))
        self.apply_filter(self.filter_combo.currentText())

    def on_download_finished(self, row):
        item = self.download_manager.get_item(row)
        if item:
            entry = {
                "name": item.title,
                "path": item.path,
                "date": datetime.datetime.now().isoformat(),
                "url": item.url,
                "quality": item.quality,
                "status": "Finished",
                "md5": item.md5
            }
            self.save_history(entry)

    def on_compress_started(self, row):
        self.update_download_row(row, 0, 0, 0, "Compressing")

    def on_compress_finished(self, row, success):
        if success:
            self.update_download_row(row, 0, 0, 0, "Compressed")
        else:
            self.update_download_row(row, 0, 0, 0, "Finished")

    def on_download_error(self, row, error):
        self.update_download_row(row, 0, 0, 0, "Error")
        QMessageBox.warning(self, "Error", f"فشل التحميل: {error}")

    def pause_download(self, row):
        self.download_manager.pause_download(row)

    def delete_download(self, row):
        self.download_manager.delete_download(row)
        self.downloads_table.removeRow(row)

    def on_table_cell_clicked(self, row, col):
        pass

    def show_context_menu(self, pos):
        index = self.downloads_table.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        item = self.download_manager.get_item(row)
        if not item or not item.finished:
            return
        menu = QMenu()
        mp3_action = menu.addAction(self.lang.get("convert_to_mp3", "Convert to MP3"))
        mp4_action = menu.addAction(self.lang.get("convert_to_720p", "Convert to 720p"))
        cut_action = menu.addAction(self.lang.get("cut_30s", "Cut first 30s"))
        compress_action = menu.addAction(self.lang.get("super_compress", "Super Compress"))
        md5_action = menu.addAction(self.lang.get("check_md5", "Check MD5"))
        action = menu.exec(self.downloads_table.viewport().mapToGlobal(pos))
        if action == mp3_action:
            self.convert_to_mp3(row)
        elif action == mp4_action:
            self.convert_to_720p(row)
        elif action == cut_action:
            self.cut_30s(row)
        elif action == compress_action:
            self.super_compress(row)
        elif action == md5_action:
            QMessageBox.information(self, "MD5", item.md5 or "غير متاح")

    def convert_to_mp3(self, row):
        item = self.download_manager.get_item(row)
        if not item:
            return
        base = os.path.join(item.path, item.title)
        input_file = self._find_file(base)
        if not input_file:
            QMessageBox.warning(self, "Error", "الملف غير موجود")
            return
        output = input_file.replace(os.path.splitext(input_file)[1], ".mp3")
        self.run_ffmpeg(input_file, output, ["-b:a", "320k"])

    def convert_to_720p(self, row):
        item = self.download_manager.get_item(row)
        if not item:
            return
        base = os.path.join(item.path, item.title)
        input_file = self._find_file(base)
        if not input_file:
            QMessageBox.warning(self, "Error", "الملف غير موجود")
            return
        output = input_file.replace(os.path.splitext(input_file)[1], "_720p.mp4")
        self.run_ffmpeg(input_file, output, ["-vf", "scale=1280:720"])

    def cut_30s(self, row):
        item = self.download_manager.get_item(row)
        if not item:
            return
        base = os.path.join(item.path, item.title)
        input_file = self._find_file(base)
        if not input_file:
            QMessageBox.warning(self, "Error", "الملف غير موجود")
            return
        output = input_file.replace(os.path.splitext(input_file)[1], "_cut.mp4")
        self.run_ffmpeg(input_file, output, ["-t", "30", "-c", "copy"])

    def super_compress(self, row):
        item = self.download_manager.get_item(row)
        if not item:
            return
        base = os.path.join(item.path, item.title)
        input_file = self._find_file(base)
        if not input_file:
            QMessageBox.warning(self, "Error", "الملف غير موجود")
            return
        output = input_file.replace(os.path.splitext(input_file)[1], "_KSO_Compressed.mp4")
        self.run_ffmpeg(input_file, output, ["-c:v", "libx265", "-crf", "28", "-preset", "fast", "-c:a", "copy"])

    def _find_file(self, base):
        for ext in [".mp4", ".mkv", ".webm", ".avi", ".mov"]:
            test = base + ext
            if os.path.exists(test):
                return test
        return None

    def run_ffmpeg(self, input_file, output_file, args):
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "Error", "الملف غير موجود")
            return
        cmd = ["ffmpeg", "-i", input_file] + args + [output_file]
        def run():
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                QMetaObject.invokeMethod(self, "show_conversion_success", Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(str, f"تم التحويل: {output_file}"))
            except subprocess.CalledProcessError as e:
                QMetaObject.invokeMethod(self, "show_conversion_error", Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(str, f"فشل التحويل: {e.stderr.decode()}"))
        threading.Thread(target=run, daemon=True).start()

    def show_conversion_success(self, msg):
        QMessageBox.information(self, "Success", msg)

    def show_conversion_error(self, msg):
        QMessageBox.warning(self, "Error", msg)

    def search_youtube(self):
        query = self.search_input.text()
        if not query:
            return
        self.load_more_btn.setEnabled(False)

        queries = {
            "all": f"ytsearch20:{query}",
            "videos": f"ytsearch20:{query} video",
            "playlists": f"ytsearch20:{query} playlist",
            "shorts": f"ytsearch20:{query} shorts"
        }

        lists = {
            "all": self.all_list,
            "videos": self.videos_list,
            "playlists": self.playlists_list,
            "shorts": self.shorts_list
        }

        def run():
            for key, yt_query in queries.items():
                ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True, 'skip_download': True}
                if self.download_manager.proxy:
                    ydl_opts['proxy'] = self.download_manager.proxy
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        results = ydl.extract_info(yt_query, download=False)
                        if results and 'entries' in results:
                            for r in results['entries']:
                                title = r.get('title', 'Unknown')
                                video_id = r.get('id', '')
                                url = f"https://youtube.com/watch?v={video_id}"
                                item = QListWidgetItem(title)
                                item.setData(Qt.ItemDataRole.UserRole, url)
                                QMetaObject.invokeMethod(lists[key], "addItem",
                                                         Qt.ConnectionType.QueuedConnection,
                                                         Q_ARG(QListWidgetItem, item))
                except Exception as e:
                    QMetaObject.invokeMethod(self, "show_error",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(str, f"فشل البحث في {key}: {e}"))
            QMetaObject.invokeMethod(self.load_more_btn, "setEnabled",
                                     Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(bool, True))
        threading.Thread(target=run, daemon=True).start()

    def search_study(self):
        query = self.study_search.text()
        if not query:
            return
        course_query = f"كورس {query}"
        queries = {
            "all": f"ytsearch20:{course_query}",
            "videos": f"ytsearch20:{course_query} video",
            "playlists": f"ytsearch20:{course_query} playlist",
            "shorts": f"ytsearch20:{course_query} shorts"
        }
        lists = {
            "all": self.study_all_list,
            "videos": self.study_videos_list,
            "playlists": self.study_playlists_list,
            "shorts": self.study_shorts_list
        }

        def run():
            for key, yt_query in queries.items():
                ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True, 'skip_download': True}
                if self.download_manager.proxy:
                    ydl_opts['proxy'] = self.download_manager.proxy
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        results = ydl.extract_info(yt_query, download=False)
                        if results and 'entries' in results:
                            for r in results['entries']:
                                title = r.get('title', 'Unknown')
                                video_id = r.get('id', '')
                                url = f"https://youtube.com/watch?v={video_id}"
                                item = QListWidgetItem(title)
                                item.setData(Qt.ItemDataRole.UserRole, url)
                                QMetaObject.invokeMethod(lists[key], "addItem",
                                                         Qt.ConnectionType.QueuedConnection,
                                                         Q_ARG(QListWidgetItem, item))
                except Exception as e:
                    QMetaObject.invokeMethod(self, "show_error",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(str, f"فشل البحث في {key}: {e}"))
        threading.Thread(target=run, daemon=True).start()

    def create_study_folder(self):
        subject = self.study_search.text()
        if not subject:
            return
        folder_name = f"كورس {subject}"
        folder_path = os.path.join(self.config["path"], folder_name)
        os.makedirs(folder_path, exist_ok=True)
        QMessageBox.information(self, "Success", f"تم انشاء المجلد: {folder_path}")

    def download_study_playlist(self):
        subject = self.study_search.text()
        if not subject:
            return
        course_query = f"كورس {subject}"
        folder_path = os.path.join(self.config["path"], f"كورس {subject}")
        os.makedirs(folder_path, exist_ok=True)

        smart_mode = self.smart_mode_check.isChecked()
        manual_threads = self.manual_threads_spin.value()
        threads = get_smart_threads(20, smart_mode, manual_threads)

        ydl_opts = {
            'extract_flat': False,
            'quiet': True,
            'skip_download': False,
            'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
            'concurrent_fragments': threads,
            'format': 'bestvideo+bestaudio',
            'merge_output_format': 'mp4',
            'noplaylist': False,
        }
        if self.download_manager.proxy:
            ydl_opts['proxy'] = self.download_manager.proxy

        def run():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"ytsearch20:{course_query}"])
                notification.notify(title="KSO", message="تم تحميل الكورس")
            except Exception as e:
                QMetaObject.invokeMethod(self, "show_error", Qt.ConnectionType.QueuedConnection, Q_ARG(str, str(e)))
        threading.Thread(target=run, daemon=True).start()

    def filter_history(self, text):
        if not text:
            return
        matches = [h for h in self.history if text.lower() in h.get("name", "").lower()]
        if matches:
            msg = "\n".join([f"{h['name']} - {h['date']}" for h in matches[:10]])
            QMessageBox.information(self, "History", msg)
        else:
            QMessageBox.information(self, "History", "لا توجد نتائج")

    def re_download_selected(self):
        text = self.history_search.text()
        if not text:
            return
        matches = [h for h in self.history if text.lower() in h.get("name", "").lower()]
        if matches:
            last = matches[-1]
            url = last.get("url")
            if url:
                self.start_download(url)
            else:
                QMessageBox.warning(self, "Error", "لا يوجد رابط لهذا الملف")
        else:
            QMessageBox.warning(self, "Error", "لم يتم العثور على ملفات")

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.lang["about"])
        dlg.resize(700, 600)
        tabs = QTabWidget()

        credits = QLabel(
            f"برمجة: {AUTHORS}\n\n"
            f"نسخة {VERSION}\n"
            "مصمم لمساعدة الطلاب في المذاكرة وتحميل الفيديوهات والـ PDF\n\n"
            "المميزات:\n"
            "- تحميل فائق السرعة مع خيوط ذكية (حتى 1,000,000 خيط)\n"
            "- مدير تحميلات متكامل مع جدولة وتصفية\n"
            "- ضاغط خارق x265 (توفير يصل إلى 90%)\n"
            "- دعم Proxy ووكيل\n"
            "- متصفح مدمج مع لقط تلقائي وحظر إعلانات\n"
            "- تشفير AES-256 للبيانات الحساسة\n"
            "- مراقبة الموارد (RAM/CPU)\n"
            "- تصدير CSV ونسخ احتياطي\n"
            "- دعم كامل للغتين العربية والإنجليزية\n"
            "- اختصارات لوحة المفاتيح الشاملة\n"
            "- دعم تحميل القنوات، البث المباشر، الشورتس\n"
            "- معاينة الفيديو وتحميل الصفحات\n"
            "- دعم السحب والإفلات"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tabs.addTab(credits, "التعريف")

        table = QTableWidget(4, 2)
        table.setHorizontalHeaderLabels(["الاختصار", "الوظيفة"])
        table.horizontalHeader().setStretchLastSection(True)
        shortcuts = [
            ("Ctrl+Shift+K", "اظهار البرنامج"),
            ("Ctrl+Shift+Q", "قفل البرنامج مع حفظ الحالة"),
            ("Ctrl+Shift+D", "تحميل الرابط من الحافظة"),
            ("Ctrl+Shift+H", "الوضع الخفي (إخفاء البرنامج)")
        ]
        for i, (key, desc) in enumerate(shortcuts):
            table.setItem(i, 0, QTableWidgetItem(key))
            table.setItem(i, 1, QTableWidgetItem(desc))
        tabs.addTab(table, "الكتالوج")

        comp = QTextEdit()
        comp.setReadOnly(True)
        comp.setPlainText(
            "مقارنة بين KSO و IDM و Snap Tube:\n\n"
            "KSO Download Turbo Ultra PRO:\n"
            "- مجاني بالكامل\n"
            "- خيوط ذكية حسب سرعة النت (حتى 1M)\n"
            "- يدعم يوتيوب، فيسبوك، تيك توك، انستا، تويتر\n"
            "- مدير تحميلات متقدم مع جدولة\n"
            "- ضاغط x265 مدمج (توفير 90%)\n"
            "- دعم Proxy وتشفير\n"
            "- واجهة عربية/إنجليزية مع وضع ليلي\n"
            "- نسخ احتياطي وتصدير CSV\n"
            "- متصفح مدمج مع حظر إعلانات\n\n"
            "IDM:\n"
            "- مدفوع\n"
            "- سرعة جيدة لكن محدودة\n"
            "- لا يدعم يوتيوب بسهولة\n"
            "- لا يدعم الضغط أو التشفير\n\n"
            "Snap Tube:\n"
            "- مجاني لكن مملوء بالإعلانات\n"
            "- سرعة محدودة\n"
            "- واجهة بسيطة جداً\n"
            "- لا يدعم الجدولة أو الوكيل\n\n"
            "الخلاصة: KSO هو الخيار الأقوى والأكثر أماناً للمستخدمين المتقدمين والطلاب."
        )
        tabs.addTab(comp, "المقارنة")

        password_widget = QWidget()
        password_layout = QVBoxLayout(password_widget)
        password_layout.addWidget(QLabel(self.lang.get("new_password", "New Password:")))
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.new_password_edit)
        save_btn = QPushButton(self.lang.get("save_password", "Save Password"))
        save_btn.clicked.connect(self.save_new_password)
        password_layout.addWidget(save_btn)
        password_layout.addStretch()
        tabs.addTab(password_widget, "كلمة السر")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        dlg.setLayout(layout)
        dlg.exec()

    def save_new_password(self):
        new_pwd = self.new_password_edit.text()
        if new_pwd:
            self.config["password"] = new_pwd
            self.password = new_pwd
            self.crypto = CryptoManager(new_pwd)
            self.save_config()
            QMessageBox.information(self, self.lang["title"], self.lang.get("password_saved", "Password saved"))
        else:
            QMessageBox.warning(self, self.lang["title"], "الرجاء إدخال كلمة سر")

    def init_hotkeys(self):
        try:
            keyboard.add_hotkey('ctrl+shift+k', self.show)
            keyboard.add_hotkey('ctrl+shift+q', self.quit_app)
            keyboard.add_hotkey('ctrl+shift+d', self.clipboard_download)
            keyboard.add_hotkey('ctrl+shift+h', self.toggle_hidden)
        except Exception as e:
            print("Hotkey error:", e)

    def clipboard_download(self):
        url = QApplication.clipboard().text()
        if url.startswith("http"):
            if QMessageBox.question(self, self.lang["title"], self.lang["download_q"] + "\n" + url) == QMessageBox.StandardButton.Yes:
                self.start_download(url)

    def toggle_hidden(self):
        if self.isVisible():
            self.hide()
            self.setWindowFlags(Qt.WindowType.Tool)
            self.show()
        else:
            self.setWindowFlags(Qt.WindowType.Window)
            self.show()

    def quit_app(self):
        self.config["path"] = self.path_btn.text()
        self.config["quality"] = self.quality_box.currentText()
        self.config["parallel"] = self.parallel_spin.value()
        self.config["shutdown"] = self.shutdown_check.isChecked()
        self.config["speed_limit"] = self.speed_limit_spin.value()
        self.config["schedule_time"] = self.schedule_edit.time().toString("HH:mm")
        self.config["password"] = self.password_edit.text()
        self.config["auto_compress"] = self.auto_compress_check.isChecked()
        self.config["smart_mode"] = self.smart_mode_check.isChecked()
        self.config["manual_threads"] = self.manual_threads_spin.value()
        self.config["proxy"] = self.proxy_edit.text().strip()
        self.config["compress_mode"] = self.compress_mode_combo.currentText()
        self.config["delete_original"] = self.delete_original_check.isChecked()
        self.config["no_duplicate"] = self.no_duplicate_check.isChecked()
        self.save_config()
        if self.shutdown_check.isChecked():
            os.system("shutdown /s /t 30")
        QApplication.quit()

    def apply_theme(self):
        hour = QTime.currentTime().hour()
        if hour >= 18 or hour < 6:
            self.setStyleSheet("""
                QMainWindow { background: #1e1e1e; color: white; }
                QToolBar { background: #2d2d2d; }
                QTableWidget { background: #252525; color: white; }
                QHeaderView::section { background: #333; color: white; }
                QPushButton { background: #3a3a3a; color: white; border: 1px solid #555; padding: 4px; }
                QLineEdit { background: #333; color: white; border: 1px solid #555; }
                QComboBox { background: #333; color: white; }
                QSpinBox { background: #333; color: white; }
                QTabWidget::pane { background: #1e1e1e; }
                QTabBar::tab { background: #333; color: white; }
            """)

    def update_yt_dlp(self):
        subprocess.Popen([sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "--quiet"])

    def show_error(self, msg):
        QMessageBox.warning(self, "Error", msg)

    def closeEvent(self, event):
        self.quit_app()
        event.accept()

# ---------- CLI Support ----------
def main_cli():
    parser = argparse.ArgumentParser(description="KSO Download Turbo Ultra CLI")
    parser.add_argument("-u", "--url", help="رابط التحميل")
    parser.add_argument("-q", "--quality", default="1080p", help="الجودة (8K, 4K, 1080p, 720p, 480p, MP3 320)")
    parser.add_argument("-o", "--output", default=os.path.expanduser("~/Downloads"), help="مسار الحفظ")
    args = parser.parse_args()
    if args.url:
        print(f"جاري تحميل: {args.url}")
        downloader = DownloadManager()
        downloader.add_download(args.url, args.output, args.quality)
        time.sleep(2)
        while True:
            time.sleep(1)
    else:
        print("يرجى توفير رابط باستخدام -u")

# ---------- Main ----------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-u", "--url"]:
        main_cli()
    else:
        app = QApplication(sys.argv)
        app.setApplicationName("KSO Download Turbo Ultra PRO")
        window = KSOApp()
        window.show()
        sys.exit(app.exec())
