import io
import threading
import urllib.request
from pathlib import Path
from typing import Union


class ThreadFileDownloader:
    """
    FileDownloader using sub thread

     url            str

     savepath(None) str,Path


    Use .get_error() to check the error
    """

    def __init__(self, url, savepath: Union[str, Path] = None):
        if savepath is not None:
            savepath = Path(savepath)
            self._partpath = savepath.parent / (savepath.name + ".part")
        else:
            self._partpath = None
        self._savepath = savepath

        self._url = url
        self._error = None
        self._file_size = None
        self._file_size_dl = None
        self._bytes = None

        threading.Thread(target=self._thread, daemon=True).start()

    def get_progress(self) -> float:
        """
        return progress of downloading as [0.0...100.0] value
        where 100.0 mean download is completed
        """
        if self._file_size is None or self._file_size_dl is None:
            return 0.0

        return (self._file_size_dl / self._file_size) * 100.0

    def get_bytes(self) -> bytes:
        """
        return bytes of downloaded file if savepath is not defined
        """
        return self._bytes

    def get_error(self) -> Union[str, None]:
        """
        returns error string or None if no error
        """
        return self._error

    def _thread(self):
        f = None
        url_req = None
        try:
            url_req = urllib.request.urlopen(self._url)
            file_size = self._file_size = int(url_req.getheader("content-length"))
            self._file_size_dl = 0
            savepath = self._savepath
            partpath = self._partpath

            if partpath is not None:
                if partpath.exists():
                    partpath.unlink()
                # Use context manager for proper file handling
                with open(partpath, "wb") as f:
                    while url_req is not None:
                        buffer = url_req.read(8192)
                        if not buffer:
                            break

                        f.write(buffer)

                        new_file_size_dl = self._file_size_dl + len(buffer)

                        if new_file_size_dl >= file_size:
                            break

                        self._file_size_dl = new_file_size_dl

                    # Complete the download
                    if self._file_size_dl >= file_size:
                        if savepath.exists():
                            savepath.unlink()
                        partpath.rename(savepath)
            else:
                # Use BytesIO for in-memory download
                with io.BytesIO() as f:
                    while url_req is not None:
                        buffer = url_req.read(8192)
                        if not buffer:
                            break

                        f.write(buffer)

                        new_file_size_dl = self._file_size_dl + len(buffer)

                        if new_file_size_dl >= file_size:
                            break

                        self._file_size_dl = new_file_size_dl

                    # Get the bytes if download completed
                    if self._file_size_dl >= file_size:
                        self._bytes = f.getvalue()

        except Exception as e:
            self._error = str(e)
            # Clean up partial file on error
            if partpath is not None and partpath.exists():
                try:
                    partpath.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
        finally:
            # Ensure URL connection is closed
            if url_req is not None:
                try:
                    url_req.close()
                except Exception:
                    pass  # Ignore close errors
