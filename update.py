import arxiv
import datetime
from qwen_api import get_response
from database import *

database = Database("./database.json")
# Construct the default API client.
client = arxiv.Client()

# Search for the 10 most recent articles matching the keyword "quantum."
search = arxiv.Search(
  query = "cs.dc OR cs.os OR cs.ar OR cs.lg",
  max_results = 20,
  sort_by = arxiv.SortCriterion.SubmittedDate
)

results = client.results(search)
all_results = list(results)
def get_id(entry_id):
    return entry_id.split("/")[-1]
articles = []
for result in all_results:
    article = Article()
    article.from_dict({
        "entry_id": get_id(result.entry_id),
        "title": result.title,
        "summary": result.summary,
        "pdf_path": None,
        "update_time": result.updated,
        "publish_time": result.published
    })
    articles.append(article)
database.add(articles)
database.translate_all()
database.dump_beautiful_markdown()
# print(len(all_results))
# prompt = "Here are 5 recent papers on AI, please look at them and give me a brief summary on each of them and a summary for all in Chinese:\n"
# for result in all_results:
#     # if date isn't today, break
#     today = datetime.datetime.now()
#     # print(result.published.date(), result.updated.date())
#     # if result.published.date() != today.date() and result.updated.date() != today.date():
#     #     break
#     prompt += f"Title: {result.title}\nAbstract: {result.summary}\n"
# prompt += "请针对以上论文，先进行一个总体的总结，然后再分别对每篇论文进行简要总结，使用学术性的中文，用自然段进行表述。"
# # print([r.title + r.summary for r in all_results])
# print(prompt)
# print(get_response(prompt))
