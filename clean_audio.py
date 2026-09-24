import os
import sys
import shutil

# Ensure FFmpeg is accessible for audio decoding (.m4a, .aac, .mp3, etc.)
def _ensure_ffmpeg_on_path():
    if shutil.which("ffmpeg"):
        return

    candidates = []
    # 1. Virtual environment Scripts directory
    venv_scripts = os.path.dirname(sys.executable)
    candidates.append(venv_scripts)

    # 2. Check Windows User / System PATH from registry (if recently installed via winget/installer)
    if sys.platform == "win32":
        try:
            import winreg
            for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    with winreg.OpenKey(root, r"Environment" if root == winreg.HKEY_CURRENT_USER else r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                        val, _ = winreg.QueryValueEx(key, "Path")
                        candidates.extend(val.split(";"))
                except OSError:
                    pass
        except Exception:
            pass

    # 3. Check imageio_ffmpeg if installed
    try:
        import imageio_ffmpeg
        candidates.append(os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()))
    except Exception:
        pass

    # Add valid paths containing ffmpeg to os.environ["PATH"]
    for path in candidates:
        path = path.strip()
        if path and os.path.isdir(path):
            if os.path.exists(os.path.join(path, "ffmpeg.exe")) or os.path.exists(os.path.join(path, "ffmpeg")):
                os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
                if shutil.which("ffmpeg"):
                    break

_ensure_ffmpeg_on_path()

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")
warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")

import librosa
import noisereduce as nr
import soundfile as sf

def reduce_background_noise(input_path, output_path):
    print(f"Loading audio file: {input_path}...")
    # Load audio; sr=None preserves the original sample rate
    audio_data, sample_rate = librosa.load(input_path, sr=None)
    
    print("Applying spectral gating noise reduction...")
    # prop_decrease controls how aggressively noise is removed (0.0 to 1.0)
    reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate, prop_decrease=1)
    
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    print(f"Saving cleaned audio to: {output_path}...")
    sf.write(output_path, reduced_noise_audio, sample_rate)
    print("Processing complete.")

if __name__ == "__main__":
    # Referencing the specific file from your local workspace
    input_file = "input/(Audio) Asana Task Automation Workflow.m4a"
    output_file = "output/Cleaned_Asana_Workflow.wav"
    
    try:
        reduce_background_noise(input_file, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        if not shutil.which("ffmpeg"):
            print("Ensure 'ffmpeg' is installed and added to your system's PATH to read .m4a files.")