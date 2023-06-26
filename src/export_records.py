import os


class ReportExporter:
    def __init__(self, output_directory):
        self.output_directory = output_directory

    def export_txt(self, meeting_name, summary, follow_ups):
        filename = f"{meeting_name}.txt"
        filepath = os.path.join(self.output_directory, filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"#{meeting_name}\n\n")
            file.write("##會議重點\n")
            file.write(summary)
            file.write("\n\n##後續行動\n")
            file.write(follow_ups)
