class RelevantDoc:
    filename: str
    relevant_score: float
    content: str

    def __init__(self, filename: str, relevant_score: float, content: str):
        self.filename = filename
        self.relevant_score = relevant_score
        self.content = content

    def __str__(self):
        return (
            f'Document name: "{self.filename}"\n'
            # f'Relevant score: {self.relevant_score}\n'
            f'Content: {self.content}\n'
        )
