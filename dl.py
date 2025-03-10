from __future__ import unicode_literals
import os
import yt_dlp
import threading
from tkinter import *
from tkinter import filedialog, messagebox

defaultDir = '~/Downloads'

class Application(Tk):
    def __init__(self, parent=None):
        Tk.__init__(self, parent)
        self.title('YouTube Converter')
        self.call('tk', 'scaling', 2.0)
        
        # Format selection (audio and video)
        self.fileFormatLst = ['audio', 'video']
        self.fileFormat = StringVar(self, 'audio')
        
        # Output directory
        self.path = os.path.expanduser(defaultDir)
        self.dirName = StringVar(self, os.path.basename(self.path))

        self.createControls()

    def createControls(self):
        Label(self, text='Select File Format').grid(row=0, column=0)
        Label(self, text='Export Directory').grid(row=0, column=2)
        
        OptionMenu(self, self.fileFormat, *self.fileFormatLst).grid(row=1, column=0)
        Button(self, text='Convert', command=self.start_conversion).grid(row=1, column=1)
        self.dirButton = Button(self, textvariable=self.dirName, command=self.changeDir)
        self.dirButton.grid(row=1, column=2)
        
        self.linkText = Text(self, width=50, height=5)
        self.linkText.grid(row=2, columnspan=3)

    def changeDir(self):
        self.path = filedialog.askdirectory(parent=self, initialdir=self.path, title='Please select a folder')
        if self.path:
            self.dirName.set(os.path.basename(self.path))

    def get_download_options(self, format_type):
        if format_type == 'audio':
            return {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': '192',
                }]
            }
        else:  # Video format
            return {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(self.path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4'
            }

    def download(self, link, format_type, failed_links):
        options = self.get_download_options(format_type)
        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                ydl.download([link])
            except Exception:
                failed_links.append(link)

    def batch_download(self, links, format_type):
        failed_links = []
        threads = []

        for link in links:
            thread = threading.Thread(target=self.download, args=(link, format_type, failed_links))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if failed_links:
            messagebox.showwarning("Warning", "Some downloads failed:
" + "
".join(failed_links))
        else:
            messagebox.showinfo("Success", f"{format_type.capitalize()} conversion complete!")

    def start_conversion(self):
        links = ''.join(self.linkText.get('1.0', 'end')).split()
        if not links:
            messagebox.showerror("Error", "Please enter at least one video URL.")
            return

        format_type = self.fileFormat.get()

        # Run batch processing in a separate thread to prevent UI freezing
        threading.Thread(target=self.batch_download, args=(links, format_type), daemon=True).start()

Application().mainloop()
