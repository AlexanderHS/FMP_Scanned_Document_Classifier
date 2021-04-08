import ghostscript
import locale

def pdf2jpeg(pdf_input_path, jpeg_output_path):
    args = ["pef2jpeg", # actual value doesn't matter
            "-dNOPAUSE",
            "-sDEVICE=jpeg",
            "-r500",
            "-sOutputFile=" + jpeg_output_path,
            pdf_input_path]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]

    ghostscript.Ghostscript(*args)

pdf2jpeg(
    "test.pdf",
    "test%03d.jpeg",
)