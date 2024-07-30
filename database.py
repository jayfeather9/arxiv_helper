import json
import arxiv
import os
import tqdm
import datetime
from typing import Optional, Union, List
from qwen_api import get_response

PDF_BASE_PATH="./database"

class Article:
    def __init__(self, entry_id: Optional[str] = None):
        if entry_id is None:
            self.entry_id = None
            self.title = None
            self.summary = None
            self.pdf_path = None
        else:
            self.entry_id = entry_id
            result = next(arxiv.Client().results(arxiv.Search(id_list=[entry_id])))
            self.title = result.title
            self.summary = result.summary
            self.pdf_path = self.find_pdf_path()
        self.cn_title = None
        self.cn_summary = None
        self.publish_time = None
        self.update_time = None
    
    def find_pdf_path(self) -> Optional[str]:
        path = os.path.join(f"{PDF_BASE_PATH}", f"{self.entry_id}.pdf")
        if os.path.exists(path):
            return path
        return None
    
    def check_pdf_path(self):
        if self.pdf_path is None or not os.path.exists(self.pdf_path):
            self.pdf_path = None
    
    def from_dict(self, data: dict):
        self.entry_id = data["entry_id"]
        self.title = data["title"]
        self.summary = data["summary"]
        self.pdf_path = data["pdf_path"]
        if "cn_title" in data and "cn_summary" in data:
            self.cn_title = data["cn_title"]
            self.cn_summary = data["cn_summary"]
        if "update_time" in data:
            self.update_time = data["update_time"]
        if "publish_time" in data:
            self.publish_time = data["publish_time"]
        self.check_pdf_path()
    
    def query_time(self):
        if self.publish_time and self.update_time:
            return
        result = next(arxiv.Client().results(arxiv.Search(id_list=[self.entry_id])))
        self.update_time = result.updated
        self.publish_time = result.published
    
    def dump(self) -> str:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "summary": self.summary,
            "pdf_path": self.pdf_path,
            "cn_title": self.cn_title,
            "cn_summary": self.cn_summary,
            "update_time": str(self.update_time) if self.update_time is not None else None,
            "publish_time": str(self.publish_time) if self.publish_time is not None else None
        }
        
    def translate(self):
        if self.cn_title is not None and self.cn_summary is not None:
            return
        self.cn_title = get_response("请使用学术性的中文将下列英文翻译为中文，不要添加任何额外信息，告诉我翻译结果即可：" + self.title)
        self.cn_summary = get_response("请使用学术性的中文将下列英文翻译为中文，不要添加任何额外信息，告诉我翻译结果即可：" + self.summary)
        

class Database:
    def __init__(self, path: str):
        self.path = path
        self.articles = {}
        self.olds = []
        self.load()
        for _, article in self.articles.items():
            article.query_time()
        
    def load(self):
        if not os.path.exists(self.path):
            # create a file
            with open(self.path, "w") as f:
                json.dump([], f)
        with open(self.path, "r") as f:
            data = json.load(f)
        for article_data in data:
            article = Article()
            article.from_dict(article_data)
            self.articles[article.entry_id] = article
            self.olds.append(article.entry_id)
    
    def dump(self):
        with open(self.path, "w") as f:
            json.dump([article.dump() for _, article in self.articles.items()], f)
    
    def add(self, articles: Union[Article, List[Article]]):
        if isinstance(articles, Article):
            articles = [articles]
        for article in articles:
            if not self.check(article.entry_id):
                self.articles[article.entry_id] = article
        self.dump()
    
    def check(self, entry_id: str) -> bool:
        return entry_id in self.articles.keys()
    
    def download_all(self):
        for _, article in self.articles.items():
            if article.pdf_path is None:
                paper = next(arxiv.Client().results(arxiv.Search(id_list=[article.entry_id])))
                paper.download_pdf(dirpath=PDF_BASE_PATH, filename=f"{article.entry_id}.pdf")
                article.pdf_path = article.find_pdf_path()
        self.dump()
    
    def translate_all(self):
        for _, article in tqdm.tqdm(self.articles.items()):
            article.translate()
        self.dump()
    
    def dump_beautiful_markdown(self):
        with open("database.md", "w") as f:
            for _, article in self.articles.items():
                f.write(f"## {article.title}\n\n")
                f.write(f"{article.summary}\n\n")
                if article.update_time is not None and article.publish_time is not None:
                    f.write(f"Published at {article.publish_time}, updated at {article.update_time}\n\n")
                if article.cn_title is not None and article.cn_summary is not None:
                    f.write(f"### {article.cn_title}\n\n")
                    f.write(f"{article.cn_summary}\n\n")
                if article.pdf_path is not None:
                    f.write(f"![PDF]({article.pdf_path})\n\n")
                f.write("\n")
    
    def dump_new_beautiful_markdown(self):
        with open("database.md", "w") as f:
            for _, article in self.articles.items():
                if article.entry_id in self.olds:
                    continue
                f.write(f"## {article.title}\n\n")
                f.write(f"{article.summary}\n\n")
                if article.update_time is not None and article.publish_time is not None:
                    f.write(f"Published at {article.publish_time}, updated at {article.update_time}\n\n")
                if article.cn_title is not None and article.cn_summary is not None:
                    f.write(f"### {article.cn_title}\n\n")
                    f.write(f"{article.cn_summary}\n\n")
                if article.pdf_path is not None:
                    f.write(f"![PDF]({article.pdf_path})\n\n")
                f.write("\n")
