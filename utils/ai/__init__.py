import openai


def fine_tune(json_file_path):
    file = openai.File.create(
        file=open(json_file_path, "rb"),
        purpose='fine-tune'
    )

    job = openai.FineTune.create(training_file=file.openai_id, model="gpt-3.5-turbo")

    print(job)


def list_jobs(job):

    response = openai.FineTune.retrieve(job)
    print(response)
