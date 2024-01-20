class RelevantDoc:
    title: str
    relevant_score: float
    body: str

    def __init__(self, title: str, relevant_score: float, body: str):
        self.title = title
        self.relevant_score = relevant_score
        self.body = body

    def __str__(self):
        return (
            f'Title: {self.title}\n'
            f'Relevant score: {self.relevant_score}\n'
            f'Body: {self.body}\n'
        )
