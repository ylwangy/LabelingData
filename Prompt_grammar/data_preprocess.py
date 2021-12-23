with open('./MAMS/cause.txt','r') as f:
    lines = f.readlines()
for text in lines:
    with open("./MAMS/test.txt", "a") as f:
        # f.write()
    # print(text)
        f.write(text.strip() + "\001cause" + "\n")
        # f.write(text + "\001For " + term.lower() + ", the sentiment is " + polarity.lower() + " .\n")
        # f.write(text + " "+"The sentiment polarity of " + term.lower() + "\t" + polarity.lower() + "\n")
        # f.write(text + "</s>"+"The " + term.lower() + " is " + "<mask>" +" ." + "\001"+ text + "</s>" + "The " + term.lower() + " is " + polarity.lower() + " .\n")

        # f.write(text + "\001The " + term.lower() + " category has a " + polarity.lower() + " label .\n")
        # f.write(text.strip() + "\001This sentence is an adverbial clause of cause .\n")
        # f.write(text + "\001The " + term.lower() + " is " + polarity.lower() + " .\n")

with open('./MAMS/purpose.txt', 'r') as f:
    lines = f.readlines()
for text in lines:
    with open("./MAMS/test.txt", "a") as f:
        # f.write()
    # print(text)
        f.write(text.strip() + "\001purpose"  + "\n")
        # f.write(text + "\001For " + term.lower() + ", the sentiment is " + polarity.lower() + " .\n")
        # f.write(text + " "+"The sentiment polarity of " + term.lower() + "\t" + polarity.lower() + "\n")
        # f.write(text + "</s>"+"The " + term.lower() + " is " + "<mask>" +" ." + "\001"+ text + "</s>" + "The " + term.lower() + " is " + polarity.lower() + " .\n")

        # f.write(text + "\001The " + term.lower() + " category has a " + polarity.lower() + " label .\n")
        # f.write(text.strip() + "\001This sentence is an adverbial clause of purpose .\n")