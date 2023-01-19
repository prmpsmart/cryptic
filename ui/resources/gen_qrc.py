from os import path, listdir, system, chdir
import shutil


def gen_qrc():
    r_d = path.dirname(__file__)
    chdir(r_d)
    qrc_path = path.join(r_d, "resources.qrc")

    qrc = open(qrc_path, "w")
    qrc.write("<RCC>\n  <qresource>\n")

    for file in listdir("."):
        if path.splitext(file)[1] not in [".qrc", ".py", ""]:
            qrc.write(f"    <file>{file}</file>\n")

    qrc.write("  </qresource>\n</RCC>")
    qrc.close()

    py_path = path.join(r_d, "resources.py")

    system(f'PySide6-rcc "{qrc_path}" -o "{py_path}"')
    shutil.move(
        py_path,
        "../resources.py",
    )


gen_qrc()
