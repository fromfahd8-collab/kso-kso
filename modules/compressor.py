import subprocess
def convert_to_mp3(input_file, output_file): subprocess.run(['ffmpeg', '-y', '-i', input_file, '-vn', '-b:a', '320k', output_file], creationflags=subprocess.CREATE_NO_WINDOW)
def convert_to_720p(input_file, output_file): subprocess.run(['ffmpeg', '-y', '-i', input_file, '-s', '1280x720', output_file], creationflags=subprocess.CREATE_NO_WINDOW)
def cut_30s(input_file, output_file): subprocess.run(['ffmpeg', '-y', '-i', input_file, '-t', '30', output_file], creationflags=subprocess.CREATE_NO_WINDOW)