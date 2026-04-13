from ragas.metrics import faithfulness, answer_relevancy
import json

# Xem toàn bộ cấu trúc prompt mặc định
print(json.dumps(faithfulness.get_prompts(), indent=2))
print(json.dumps(answer_relevancy.get_prompts(), indent=2))