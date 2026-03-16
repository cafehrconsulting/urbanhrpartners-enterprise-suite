from xiomy.core.xiomy_brain import XiomyBrain

# create XIOMY brain
brain = XiomyBrain()

print("System Status:")
print(brain.system_status())

print("\nGreeting:")
print(brain.greeting())

print("\nProcessing Message:")
print(brain.process_message("show me crm clients"))
