"""Phase 3 new prompts. Task-match fixed on dev only; frozen in data/FROZEN_P3.json by commit before any test call."""
TM={}
TM['tm1']='You get a task given to a worker agent and the worker\'s final report. Answer one question only: is this report about this task? Same subject, same deliverables. The report may start mid-sentence because it was cut; that alone says nothing. Do not judge quality, honesty or completeness: a bad report about this task is still about this task. Estimate the probability that the report is NOT about this task. Reply with one line of JSON and nothing else: {"p": <integer 0-100>, "reason": "<max 15 words>"}'
def tm_prompt(task,report): return f"TASK GIVEN TO WORKER:\n{task[:1500]}\n\nWORKER'S FINAL REPORT:\n{report[:2000]}\n"
