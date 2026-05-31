from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


PAGE_SIZES = {
    "A4": (2480, 3508),
    "A3": (3508, 4961),
    "Letter": (2550, 3300),
}


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def cm_to_px(cm: float, dpi: int = 300) -> int:
    return int((cm / 2.54) * dpi)


class GridGenerator:

    def __init__(
        self,
        page_size="A4",
        cols=2,
        rows=3,
        margin_cm=1.0,
        padding_cm=0.3,
        dpi=300,
        show_page_numbers=True,
        background_color="white",
    ):

        self.page_size = page_size
        self.cols = cols
        self.rows = rows
        self.margin_cm = margin_cm
        self.padding_cm = padding_cm
        self.dpi = dpi
        self.show_page_numbers = show_page_numbers
        self.background_color = background_color

    @property
    def images_per_page(self):
        return self.cols * self.rows

    def get_image_files(self, image_folder):

        image_folder = Path(image_folder)

        if not image_folder.exists():
            return []

        return sorted(
            [
                p
                for p in image_folder.iterdir()
                if p.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )

    def generate_pages(self, image_folder):

        image_files = self.get_image_files(image_folder)

        if not image_files:
            return []

        page_width, page_height = PAGE_SIZES[self.page_size]

        margin = cm_to_px(
            self.margin_cm,
            self.dpi,
        )

        padding = cm_to_px(
            self.padding_cm,
            self.dpi,
        )

        usable_width = (
            page_width
            - (margin * 2)
            - ((self.cols - 1) * padding)
        )

        usable_height = (
            page_height
            - (margin * 2)
            - ((self.rows - 1) * padding)
        )

        cell_width = usable_width // self.cols
        cell_height = usable_height // self.rows

        pages = []

        for start in range(
            0,
            len(image_files),
            self.images_per_page,
        ):

            page_index = (
                start // self.images_per_page
            ) + 1

            page = Image.new(
                "RGB",
                (page_width, page_height),
                self.background_color,
            )

            batch = image_files[
                start : start + self.images_per_page
            ]

            for idx, image_path in enumerate(batch):

                row = idx // self.cols
                col = idx % self.cols

                x0 = (
                    margin
                    + col * (cell_width + padding)
                )

                y0 = (
                    margin
                    + row * (cell_height + padding)
                )

                try:

                    img = Image.open(
                        image_path
                    ).convert("RGB")

                    img.thumbnail(
                        (
                            cell_width,
                            cell_height,
                        ),
                        Image.Resampling.LANCZOS,
                    )

                    paste_x = (
                        x0
                        + (
                            cell_width
                            - img.width
                        )
                        // 2
                    )

                    paste_y = (
                        y0
                        + (
                            cell_height
                            - img.height
                        )
                        // 2
                    )

                    page.paste(
                        img,
                        (
                            paste_x,
                            paste_y,
                        ),
                    )

                except Exception as e:

                    print(
                        f"Failed: {image_path}"
                    )
                    print(e)

            if self.show_page_numbers:
                self._draw_page_number(
                    page,
                    page_index,
                )

            pages.append(page)

        return pages

    def _draw_page_number(
        self,
        page,
        page_number,
    ):

        draw = ImageDraw.Draw(page)

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                40,
            )
        except:
            font = ImageFont.load_default()

        text = f"Page {page_number}"

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        page_width, page_height = page.size

        x = (
            page_width - text_width
        ) // 2

        y = page_height - 80

        draw.text(
            (x, y),
            text,
            fill="black",
            font=font,
        )

    def export_pages(
        self,
        pages,
        output_folder,
        image_format="JPG",
        quality=95,
    ):

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        exported_files = []

        image_format = (
            image_format.upper()
        )

        extension = (
            ".png"
            if image_format == "PNG"
            else ".jpg"
        )

        for idx, page in enumerate(
            pages,
            start=1,
        ):

            file_path = (
                output_folder
                / f"page_{idx:03d}{extension}"
            )

            if image_format == "PNG":

                page.save(
                    file_path,
                    format="PNG",
                )

            else:

                page.save(
                    file_path,
                    format="JPEG",
                    quality=quality,
                )

            exported_files.append(
                file_path
            )

        return exported_files