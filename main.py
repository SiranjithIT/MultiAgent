from agents import WorkflowManager

while True:
  user_query = input("Enter your query('exit' to quit): ")
  
  if user_query == 'exit':
    break
  
  manager = WorkflowManager()
  response = manager.run(user_query)
  
  print(response)