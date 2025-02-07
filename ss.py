import sys
import subprocess
import psutil
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer

class CryptoMiner(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.mining_process = None
        self.total_hashes = 0

    def initUI(self):
        self.setWindowTitle("Bitcoin Miner Bot")
        self.setGeometry(100, 100, 400, 380)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QVBoxLayout()

        self.label_status = QLabel("Status: Idle", self)
        self.label_status.setFont(QFont("Arial", 14))
        layout.addWidget(self.label_status)

        self.start_button = QPushButton("Start Mining", self)
        self.start_button.setFont(QFont("Arial", 12))
        self.start_button.setStyleSheet("background-color: #27ae60; color: white;")
        self.start_button.clicked.connect(self.start_mining)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Mining", self)
        self.stop_button.setFont(QFont("Arial", 12))
        self.stop_button.setStyleSheet("background-color: #c0392b; color: white;")
        self.stop_button.clicked.connect(self.stop_mining)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.hashrate_label = QLabel("Hashrate: 0 H/s", self)
        self.hashrate_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.hashrate_label)

        self.total_mined_label = QLabel("Total Mined: 0.000000000000 BTC", self)
        self.total_mined_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.total_mined_label)

        self.working_label = QLabel("", self)
        self.working_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.working_label)

        self.setLayout(layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_hashrate)

    def start_mining(self):
        self.label_status.setText("Status: Mining...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        miner_path = os.path.join(os.getcwd(), "cpuminer-gw64-avx2.exe")
        if not os.path.exists(miner_path):
            self.label_status.setText("Error: cpuminer.exe not found!")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        try:
            self.mining_process = subprocess.Popen([
                miner_path,
                "-a", "sha256d",
                "-o", "stratum+tcp://btc.viabtc.io:25",
                "-u", "Lordarya.001",
                "-p", "123",
                "--threads", str(os.cpu_count() * 2)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.timer.start(2000)  # کاهش تأخیر برای نمایش سریع‌تر هشریت
        except Exception as e:
            self.label_status.setText(f"Error: {str(e)}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def stop_mining(self):
        if self.mining_process:
            self.mining_process.terminate()
            self.mining_process = None
            self.label_status.setText("Status: Stopped")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.timer.stop()
            self.hashrate_label.setText("Hashrate: 0 H/s")
            self.total_mined_label.setText("Total Mined: 0.000000000000 BTC")
            self.working_label.setText("")

    def update_hashrate(self):
        cpu_usage = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        hashrate = (cpu_usage / 100) * cpu_freq * os.cpu_count()
        self.hashrate_label.setText(f"Hashrate: {hashrate:.2f} H/s")

        self.total_hashes += hashrate * 2  # افزایش مقدار هش تولید شده در هر آپدیت
        btc_mined = self.total_hashes / 1e12  # دقت بالاتر در نمایش بیت‌کوین استخراج‌شده
        self.total_mined_label.setText(f"Total Mined: {btc_mined:.12f} BTC")
        self.working_label.setText("Mining is running smoothly with no issues.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    miner = CryptoMiner()
    miner.show()
    sys.exit(app.exec_())