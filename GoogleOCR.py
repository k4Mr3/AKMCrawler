import os
from google.cloud import vision


def detect_document(path):
    client = vision.ImageAnnotatorClient()

    file_list = os.listdir(path)

    sorted_file_list = sorted(file_list, key=lambda x: int(x.split(".")[0]))

    with open(path + ".txt", "a") as file:

        for filename in sorted_file_list:
            if filename.endswith(".jpg"):

                number_str = ''.join(filter(str.isdigit, filename))
                number = int(number_str)


                if (number > 0):
                    print(f"Przetwarzam plik {filename}")
                    with open(path + "/" + filename, "rb") as image_file:
                        content = image_file.read()

                    image = vision.Image(content=content)

                    response = client.document_text_detection(image=image)

                    strona = ""

                    for page in response.full_text_annotation.pages:
                        for block in page.blocks:

                            for paragraph in block.paragraphs:

                                if paragraph.confidence > 0.7:

                                    for word in paragraph.words:
                                        word_text = "".join([symbol.text for symbol in word.symbols])

                                        strona += word_text + " "

                    file.write('\n\nStrona ' + filename + '\n\n')
                    file.write(strona)

                    if response.error.message:
                        raise Exception(
                            "{}\nFor more info on error messages, check: "
                            "https://cloud.google.com/apis/design/errors".format(response.error.message)
                        )


# Nazwa folderu z plikami od 1.jpg do n.jpg
detect_document('AG15')

