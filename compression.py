import bz2
import gzip
import lzma
import os
import shutil
import subprocess
import sys
import timeit
import zlib

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from ebooklib import epub
from mutagen.id3 import ID3, delete
from mutagen.mp3 import MP3


# Functions to remove metadata from various file types
def remove_pdf_metadata(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})
    with open(output_pdf_path, 'wb') as f:
        writer.write(f)


def remove_image_metadata(input_image_path, output_image_path, ):
    image = Image.open(input_image_path)
    data = list(image.getdata())
    image_without_metadata = Image.new(image.mode, image.size)
    image_without_metadata.putdata(data)
    image_without_metadata.save(output_image_path)


def remove_audio_metadata(input_audio_path, output_audio_path, ):
    audio = MP3(input_audio_path, ID3=ID3)
    delete(audio)
    audio.save(output_audio_path)


def remove_video_metadata(input_video_path, output_video_path, ):
    subprocess.run(['ffmpeg', '-i', input_video_path, '-map_metadata', '-1', '-c:v', 'copy', '-c:a', 'copy',
                    output_video_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def remove_docx_metadata(input_docx_path, output_docx_path):
    doc = Document(input_docx_path)
    core_properties = doc.core_properties
    core_properties.author = None
    core_properties.title = None
    core_properties.subject = None
    core_properties.keywords = None
    core_properties.comments = None
    doc.save(output_docx_path)


def remove_epub_metadata(input_epub_path, output_epub_path):
    book = epub.read_epub(input_epub_path)
    book.set_title(None)
    book.set_author(None)
    book.set_language(None)
    epub.write_epub(output_epub_path, book)


def remove_metadata(input_path, output_path):
    file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if file_size_mb <= 20:
        print(f"File size is {file_size_mb:.2f} MB, skipping metadata removal.")
        return 0, input_path

    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    output_path = f'output{ext}'

    if ext == '.pdf':
        return timeit.timeit(lambda: remove_pdf_metadata(input_path, output_path), number=1), output_path
    elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
        return timeit.timeit(lambda: remove_image_metadata(input_path, output_path), number=1), output_path
    elif ext == '.mp3':
        return timeit.timeit(lambda: remove_audio_metadata(input_path, output_path), number=1), output_path
    elif ext in ['.mp4', '.avi', '.mkv']:
        return timeit.timeit(lambda: remove_video_metadata(input_path, output_path), number=1), output_path
    elif ext == '.docx':
        return timeit.timeit(lambda: remove_docx_metadata(input_path, output_path), number=1), output_path
    elif ext == '.epub':
        return timeit.timeit(lambda: remove_epub_metadata(input_path, output_path), number=1), output_path
    else:
        start_time = timeit.default_timer()
        shutil.copy(input_path, output_path)
        return timeit.default_timer() - start_time,output_path


# Example usage for removing metadata and measuring the time taken
input_path = 'currency.png'
output_path = ''
time_taken, output_path = remove_metadata(input_path, output_path)
print(f"Time taken to remove metadata: {time_taken:.6f} seconds")

# Read the processed PDF file
with open(output_path, 'rb') as f:
    data = f.read()


# Functions to compress data using different algorithms
def compress_zlib(data):
    return zlib.compress(data)


def compress_gzip(data):
    return gzip.compress(data)


def compress_bz2(data):
    return bz2.compress(data)


def compress_lzma(data):
    return lzma.compress(data)


# Measure compression time
time_zlib = timeit.timeit(lambda: compress_zlib(data), number=10)
time_gzip = timeit.timeit(lambda: compress_gzip(data), number=10)
time_bz2 = timeit.timeit(lambda: compress_bz2(data), number=10)
time_lzma = timeit.timeit(lambda: compress_lzma(data), number=10)

# Measure compressed size
size_zlib = sys.getsizeof(compress_zlib(data))
size_gzip = sys.getsizeof(compress_gzip(data))
size_bz2 = sys.getsizeof(compress_bz2(data))
size_lzma = sys.getsizeof(compress_lzma(data))

# Original size
original_size = sys.getsizeof(data)

# Calculate compression ratios as percentages
ratio_zlib = (original_size - size_zlib) / original_size * 100
ratio_gzip = (original_size - size_gzip) / original_size * 100
ratio_bz2 = (original_size - size_bz2) / original_size * 100
ratio_lzma = (original_size - size_lzma) / original_size * 100

print(f"zlib: time = {time_zlib:.6f}s, size = {size_zlib} bytes, ratio = {ratio_zlib:.2f}%")
print(f"gzip: time = {time_gzip:.6f}s, size = {size_gzip} bytes, ratio = {ratio_gzip:.2f}%")
print(f"bz2:  time = {time_bz2:.6f}s, size = {size_bz2} bytes, ratio = {ratio_bz2:.2f}%")
print(f"lzma: time = {time_lzma:.6f}s, size = {size_lzma} bytes, ratio = {ratio_lzma:.2f}%")
