from dotenv import load_dotenv
load_dotenv() #important:确保.env被加载
from apps import create_app

if __name__ == '__main__':
    app = create_app()
    app.run()