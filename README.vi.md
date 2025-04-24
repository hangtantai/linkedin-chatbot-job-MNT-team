# <img src="https://github.com/user-attachments/assets/cac75d32-c147-4c2f-bfbc-c01fc7cb12d8" width="50" height="50" bottom-padding="0"> Project Title: Linkedin Chatbot Job
<p align="center">
  <a href="README.md">English</a> |
  <a href="README.vi.md">Tiếng Việt</a>
</p>


<a id="vietnamese"></a>
# 📌 Overview [Tiếng Việt]:
Dự án này được phát triển bởi nhóm MNT (Math and Technology), một nhóm trẻ với đam mê công nghệ và toán học từ trường Đại học Khoa học Tự nhiên (University of Science), đại học Quốc Gia Thành phố Hồ Chí Minh, với mong muốn tìm hiểu và ứng dụng các công cụ AI. Đây là một dự án nhỏ nhưng có mục tiêu rõ ràng: nghiên cứu, triển khai một AI với data từ Linkedin để phục vụ cho mọi người có thể search về chi tiết job và nhờ AI chuẩn bị giúp về yêu cầu, kỹ năng mềm,... hay đơn giản là so sánh giữa các job với nhau. Chúng tôi mong muốn tạo ra một nền tảng có tính thực tiễn cao, đồng thời học hỏi và chia sẻ kiến thức với tất cả mọi người. 

**Lưu ý 1: Vì đây là 1 dự án phi lợi nhuận nên các công cụ đều là free-plan, chủ yếu nhắm vào kỹ thuật được nghiên cứu và sử dụng trong kiến trúc, có thể sẽ có 1 vài vấn đề với câu trả lời không bằng như xài các model trả phí, mong được mọi người thông cảm.**

**Lưu ý 2: Bởi vì tạo 1 tài khoản để chat thì tụi mình chưa có kinh nghiệm và việc quản lý chat để tránh bị mất token hay đầy bộ nhớ nên tụi mình sẽ đóng lại và chỉ show code và demo, sau này tụi mình sẽ phát triển trên Kubernetes để tạo 1 web/app cho mọi người sử dụng**

**Lưu ý 3: Kiến thức công nghệ sẽ update ở đây [document](/document/)**


# 📁 Project Structure
```linkedin-chatbot-job-MNT-team/
├── .devcontainer/             # Development container configuration
├── .streamlit/                # Streamlit configuration with secrets.toml
├── document/                  # Project documentation
├── images/                    # Images for README and documentation
├── streamlit_app/             # Main application code
│   ├── app/                   # Streamlit application core
│   ├── db/                    # Database handlers
│   │   └── vector_db/         # Vector database files
│   ├── handlers/              # Request handlers
│   │   └── chat_modules/      # Chat functionality modules
│   ├── helpers/               # Helper functions
│   ├── static/                # Static assets
│   └── utils/                 # Utility functions
│       └── logs/              # Application logs
├── vector_database/           # RAG pipeline implementation
└── web_scrapping/             # LinkedIn data scraping module
    ├── chromedriver-win64/    # Chrome webdriver
    ├── commands/              # Command pattern implementations
    ├── db/                    # Database interactions
    ├── downloaded_files/      # Downloaded job data
    ├── driver/                # Selenium driver wrappers
    ├── factories/             # Factory pattern implementations
    ├── helpers/               # Helper utilities 
    ├── repository/            # Data access layer
    ├── strategies/            # Strategy pattern implementations
    └── utils/                 # Utility functions
        └── logs/              # Scraping logs
```

# 🌟 Features: 
## 1. Web Scrapping:
Lấy tất cả thông tin từ job liên quan về từ khóa: tất cả các keyword về công nghệ (Computer Science and Technology).
- Automation ETL với selenium để lấy toàn bộ thông tin về job.
- Sử dụng airflow để tự động quá trình này.

## 2. Xây dựng RAG pipeline:
Trước khi đóng gói tất cả các vector database thành file pkl thì chúng ta sẽ xử lý các bước như:
- Tạo Document
- Split Document cho việc dễ xử lý
- Khởi tạo Retriever và fit vào Document
- Lưu thành file pkl và load lên S3 để lưu lại
- Khi Chatbot khởi tạo retriever thì sẽ download về và sử dụng

## 3. AI chatbot:
Dự án có các chức năng cơ bản như:
- Tạo new chat.
- Xóa chat.
- Chat về job mới nhất trên linkedin, search theo keyword, so sánh benefit, roadmap cho từng nghành nghề, techniques cần chuẩn bị.
- Xem lịch sử chat (không phát triển phần này vì nhóm chúng mình không có role chuyên về frontend và backend nên việc tạo 1 account là rất khó khăn nên **hệ thống sẽ tự động xóa chat kể từ 3 ngày cho lần chat đầu tiên**)

# 🎥 Demo website:
Image Demo:

Giao diện
![Interface](images/interface.png)

Khi mọi thứ load thành công
![Load](images/load.png)

Giao diện chat
![Chat](images/chat.png)

Yêu cầu số 1: bằng English
![Sample 1](images/sample1.png)

Yêu cầu số 2: bằng English
![Sample 2](images/sample2.png)

Yêu cầu số 3: bằng Vietnamese
![Sample 1](images/sample3.png)


Link trải nghiệm: https://linkedin-chatbot-job-mnt-team.streamlit.app/ (Vì streamlit sẽ đóng các ứng dụng nặng nên tụi mình sẽ đóng lại)

# 🛠️ Installation:
## Clone project
```bash
git clone <link to github project>
```

## Installation necessary package
```python
pip install -r requirements.txt
```

# Set up environment
## Create a folder .streamlit (recommend)
Sau đó bạn hãy tạo 1 file secrets.toml, bạn cần tạo các API sau

### WebScrapping: Linkedin
EMAIL="your_username"
PASSWORD="your_password"

### APP: GROQ API: LLM MODEL
GROQ_API_KEY="your_api"

### APP: MONGO_URI: Memory chat
MONGO_URI="your_api"

### APP: AIVEN: Database (phía dưới có hướng dẫn cách tạo và quick connect, phần database)
HOST_AIVEN="your_api" \
USER_AIVEN="your_api" \
PASSWORD_AIVEN="your_api" \
DB_AIVEN="your_api"\
PORT_AIVEN="your_api"\
TABLE_AIVEN="your_api"

### APP: AWS S3: Saving object data (phía dưới phần database có hướng dẫn)
S3_BUCKET_JOB="your_api"\
S3_BUCKET_LOG="your_api"\
S3_BUCKET_VECTORDB="your_api"\
PREFIX_VECTORDB="your_api"\
AWS_ACCESS_KEY_ID="your_api"\
AWS_SECRET_ACCESS_KEY="your_api"

### APP: COHERE: ranking function
COHERE_API_KEY="your_api"\

## Create a file .env (not recommend)
Bạn vẫn tạo 1 file và điền các thông tin như trên nhưng cần phải chỉnh khá nhiều, vì tụi mình build trên streamlit nên tụi mình xài .streamlit secrets luôn thay vì environment như các dự án thông thường.

# ⚙️ Usage:

## Run command to set up project
```bash
pip install -e .
```

## Web Scrapping: 
bởi vì lý do là Linkedin đã áp dụng những capcha, làm chúng tôi khó khăn chạy lệnh này, nên chúng tôi đã dừng lại phát triển web_scrapping, bạn có thể tham khảo
```bash
cd "<current_path>/linkedin-chatbot-job-MNT-team/web_scrapping"
python main.py
```
or
```bash
python "<current_path>/linkedin-chatbot-job-MNT-team/web_scrapping/main.py"
```

## Without Web Scraping: because we have scrapped, you can use it 
- Bạn có thể tìm data của chúng tôi đã cào tại  /web_scrapping/processed_data.csv, nó chứa khoảng 300 data sample job được lấy từ Linkedin (ngày kết thúc cào 23/4/2025)
- Nếu bạn không chạy lệnh cào, thì nó sẽ không push lên s3, thì bạn cần push lên s3 với file /web_scrapping/load_data.py

## AI chatbot:
**Chạy Vectordatabase (Manual)**
```bash
cd "<current_path>/linkedin-chatbot-job-MNT-team/vector_database"
python rag.py
```
or
```bash
python "<current_path>/linkedin-chatbot-job-MNT-team/vector_database/rag.py"
```

**Chạy app**
```bash
streamlit run streamlit_app/app/main.py
```

# 🏗️ Architecture for this project:
## Web Scrapping
![Alt text](images/web_scrapping.png)


## Vector Database
![Alt text](images/vectordb.png)

## App
![Alt text](images/app.png)

## Flow AI
![Alt text](images/flow-ai.png)

# 📊 Database Core:
## Database Schema:
![Alt text](images/database.png)

## Connect to Aiven:
Chúng tôi sử dụng Aiven platform, DBMS sử dụng là MySQL, với cấu hình là:
- 1 CPU
- 1 GB RAM (processing)
- 5 GB Storage

là bản free-plan hỗ trợ cho các dự án phi lợi nhuận, tham khảo tại đây: https://console.aiven.io/
- Nếu bạn tự tạo database, thì bạn có thể vào service của bạn và nhấn vào quick connnect và chọn python.
- Còn nều bạn không phải owner, thì aiven có feature là add user vào.
- Aiven hiện tại không có feature view table trên chính nền tảng của họ, nên chỉ có thể sử dụng code với các command để check.

## Database for Memory Chat:
Chúng tôi sử dụng Mongo Atlas, là phiên bản mongodb nhưng trên cloud hỗ trợ rất nhiều cho developer phát triển.
Một số lưu ý khi bạn sử dụng mongo atlas:
- Nếu muốn connect thì bạn cần URI, và mongo atlas bảo mật rất tốt nên chỉ có thể sử dụng connection (0.0.0.0, tức là cho phép mọi địa chỉ IP truy cập vào), thông thường sẽ bị chặn toàn bộ IP, trừ IP local của bạn.
- Nên xem kĩ các dung lượng lưu trữ của Mongo atlas, vì free-plan nên giới hạn cũng khá nhiều, bạn không thể sử dụng VPC hay các cách kết nối nâng cao khác ngoài 0.0.0.0, nếu xài free-plan.

## AWS S3
Kết nối vào S3, thì các bạn cần đăng nhập và lấy được các thông tin sau:
- Vào IAM
- Tạo access keys
- Tạo xong thì copy 2 phần là: AWS Access key ID và AWS secret access key
- S3 thì bạn cần tạo thêm bucket trong s3, nếu bạn cần tạo folder ví dụ FAISS, thì phải có folder riêng với BM25, nên sẽ có 1 prefix là vector_database/faiss

# 🔧 Công Nghệ Sử Dụng:
- **Selenium**: Tự động hóa web cho việc trích xuất dữ liệu
- **Apache Airflow**: Điều phối quy trình ETL
- **LangChain**: Framework để xây dựng RAG pipeline
- **FAISS/BM25**: Cơ sở dữ liệu vector để tìm kiếm tương đồng
- **AWS S3**: Lưu trữ dữ liệu và mô hình
- **MongoDB Atlas**: Lưu trữ lịch sử chat
- **MySQL (Aiven)**: Cơ sở dữ liệu quan hệ
- **Streamlit**: Framework ứng dụng web
- **GROQ**: Nhà cung cấp LLM
- **Python**: Ngôn ngữ lập trình cốt lõi

# 🤝 Contributing:
Leader: Hàng Tấn Tài (US)

Member: Nguyễn Hoàng Nam (US)

Member: Hồ Quốc Tuấn (US)

# 📝 License:
![License](https://img.shields.io/badge/License-MIT-blue.svg)  
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

# 🙏 Thank you! Donate for my team!!