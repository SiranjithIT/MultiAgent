from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults

wrapper = DuckDuckGoSearchAPIWrapper(time="d", max_results=6)
search = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")

if __name__ == "__main__":
  result = search.invoke("Gen AI")
  result.extend(search.invoke("Agent AI"))
  for i in result:
    print(i, end="\n\n")