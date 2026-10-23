
Relevance floor stats

0.6 answerable refused: 0 of 40 | unanswerable refused: 2 of 10
0.625 answerable refused: 0 of 40 | unanswerable refused: 2 of 10
0.63 answerable refused: 0 of 40 | unanswerable refused: 3 of 10
0.635 answerable refused: 0 of 40 | unanswerable refused: 3 of 10 
0.65 answerable refused: 4 of 40 | unanswerable refused: 6 of 10
0.675 answerable refused: 8 of 40 | unanswerable refused: 8 of 10
0.685 answerable refused: 9 of 40 | unanswerable refused: 8 of 10
0.7 answerable refused: 13 of 40 | unanswerable refused: 9 of 10

---
R@1, R@3, R@5, MRR, ctx, ans & unans

whole_document      R@1 0.9 R@3 1 R@5 1 MRR 0.95 ctx 582 ans 0.606 unans 0.546
fixed_100            R@1 0.6 R@3 0.725 R@5 0.75 MRR 0.655 ctx 262 ans 0.631 unans 0.541
fixed_overlap_25     R@1 0.725 R@3 0.925 R@5 0.95 MRR 0.815 ctx 258 ans 0.633 unans 0.543
sentences_100        R@1 0.575 R@3 0.8 R@5 0.85 MRR 0.686 ctx 245 ans 0.629 unans 0.536
sections_plain       R@1 0.55 R@3 0.65 R@5 0.725 MRR 0.609 ctx 77 ans 0.626 unans 0.503
sections_contextual  R@1 0.825 R@3 0.975 R@5 1 MRR 0.898 ctx 117 ans 0.719 unans 0.627

---

Claude Haiku, 0.635 relevance floor 

whole_document {'answer_accuracy': 0.35, 'refusal_accuracy': 1, 'false_refusals': ['q02', 'q03', 'q04', 'q06', 'q09', 'q10', 'q11', 'q12', 'q13', 'q17', 'q18', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q28', 'q29', 'q32', 'q35', 'q36', 'q37', 'q38', 'q40'], 'wrong_or_unrefused': ['q08'], 'truncated': [], 'model_calls': 16, 'avg_input_tokens': 539}

sections_contextual {'answer_accuracy': 0.975, 'refusal_accuracy': 1, 'false_refusals': [], 'wrong_or_unrefused': ['q20'], 'truncated': [], 'model_calls': 47, 'avg_input_tokens': 334}

fixed_overlap_25 {'answer_accuracy': 0.375, 'refusal_accuracy': 1, 'false_refusals': ['q01', 'q02', 'q03', 'q06', 'q08', 'q09', 'q12', 'q13', 'q17', 'q18', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q28', 'q29', 'q32', 'q33', 'q35', 'q36', 'q37', 'q38'], 'wrong_or_unrefused': ['q34'], 'truncated': [], 'model_calls': 18, 'avg_input_tokens': 378}

---

The relevance floor finds it quite difficult to separate unanswerable questions because the questions in  my eval set which are labelled unanswerable are still relate heavily to some elements within the docs. 

I believe this makes my relevance floor even stronger because although it is only able to refuse 30% of the unanswerable questions, it is sure to refuse questions that are clearly unrelated and the model does a very good job of receiving the 70% of  unanswerable questions that pass the floor and refusing them.

---

Explain that after using multiple models and getting subpar answer accuracy results, I realized the models where not failing but my keyword guardrail in the eval set was too strict in a number of cases so I loosened the requirements so genuinely correct answers correctly pass the eval set.
