import os
import subprocess
import google.generativeai as genai
import time
import re # reモジュールをインポート

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY 環境変数が設定されていません。実行する前に設定してください。")

genai.configure(api_key=GEMINI_API_KEY)

try:
    with open("prompt.txt", "r") as f:
        pre_prompt = f.read()
except FileNotFoundError:
    raise FileNotFoundError("prompt.txt が見つかりません。必要なシステムプロンプトを含むファイルを作成してください。")


def get_gemini_response(user_input):
    # gemini-2.0-flash-lite, gemini-1.5-flash
    model = genai.GenerativeModel('gemini-2.0-flash-lite')

    chat = model.start_chat(history=[
        {"role": "user", "parts": [pre_prompt]},
        {"role": "model", "parts": ["はい、あなたの指示に基づいてROS 2用のPythonコードを生成します。コマンドを入力してください。"]}
    ])

    try:
        response = chat.send_message(user_input)
        #print(f"\n--- Geminiからの生の応答 ---\n{response.text.strip()}\n--------------------------\n")
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API呼び出し中にエラーが発生しました: {e}")
        return None

def generate_python_script(res):
    if res is None:
        print("コードが生成されませんでした。スクリプトの作成をスキップします。")
        return None
    
    python_code = res
    match = re.search(r'```python\n(.*?)```', python_code, re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()
    else:
        print("```python```形式のコードブロックが見つかりませんでした。応答全体をコードとして扱います。")
        extracted_code = python_code.strip()

    print(f"\n--- 抽出されたPythonコード ---\n{extracted_code}\n----------------------------\n")

    file_name = "generated_script.py"
    with open(file_name, "w") as f:
        f.write(extracted_code)
    print(f"\n生成されたコードは {file_name} に保存されました。\n")
    return file_name

# subprocessでpythonスクリプトを実行する
def run_python_script(script_path):
    if script_path is None:
        return
    
    print(f"{script_path} を実行中...")
    try:
        result = subprocess.run(
            ["python3", script_path], 
            capture_output=True, 
            text=True,
            check=False
        )
        if result.returncode != 0:
            print(f"スクリプトの実行中にエラーが発生しました: コマンド '['python3', '{script_path}']' はゼロ以外の終了ステータス {result.returncode} を返しました。")
        
        print(f"標準出力:\n{result.stdout}")
        if result.stderr:
            print(f"標準エラー出力:\n{result.stderr}")

    except FileNotFoundError:
        print(f"エラー: Pythonインタープリタまたはスクリプトが見つかりません。'python3'がPATHにあり、'{script_path}'が存在することを確認してください。")
    except Exception as e:
        print(f"スクリプト実行中に予期せぬエラーが発生しました: {e}")
    print("-" * 30)

def main_loop():
    print("TurtleBot3 のコマンドを入力してください ('exit' と入力すると終了します):")
    while True:
        user_command = input("> ")
        if user_command.lower() == 'exit':
            print("プログラムを終了します。")
            break
        
        generated_code_response = get_gemini_response(user_command)
        
        script_file_path = generate_python_script(generated_code_response)

        if script_file_path:
            run_python_script(script_file_path)

        time.sleep(2)

if __name__ == "__main__":
    main_loop()
