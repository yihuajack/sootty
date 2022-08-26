import os, sys
from sootty.exceptions import SoottyError
import datetime
import yaml


def save_query(save, name, wires, br, length, start, end, output):
    savefile = os.getenv("HOME") + "/.config/sootty/save/queries.yaml"

    if is_save_file(savefile):
        """
        Memory check for the file
        """
        with open(savefile, "r+") as f:
            lines = yaml.safe_load(f)
        if lines is None:
            with open(savefile, "w") as stream:
                query_write(
                    savefile, stream, save, name, wires, br, length, start, end, output
                )
        else:
            if save in lines:
                pass
            else:
                if len(lines) >= 500:
                    print(
                        "Saved query limit reached. Deleting least recent query to accommodate new query.",
                        file=sys.stderr,
                    )
                    f.truncate(0)
                    for key in lines:
                        stat = lines.pop(key)
                        break
                    if stat is None:  # No lines to delete/Error
                        raise SoottyError("Error deleting least recent query.")
                    yaml.dump(lines, f, sort_keys=False, width=float("inf"))

            with open(savefile, "a+") as stream:
                query_write(
                    savefile, stream, save, name, wires, br, length, start, end, output
                )

    else:
        # Creating new savefile as no savefiles found for sootty
        print("Creating new savefile...")
        with open(savefile, "w") as stream:
            query_write(
                savefile, stream, save, name, wires, br, length, start, end, output
            )


def query_write(
    savefile_path, savefile, save, name, wires, br, length, start, end, output
):
    with open(savefile_path, "r") as stream:
        lines = yaml.safe_load(stream)
        if lines is None or (not save in lines):
            savefile.write(save + ":\n")
            savefile.write("  query:")
            savefile.write(query_build(name, wires, br, length, start, end, output))
            savefile.write("\n")
            savefile.write("  date: " + str(datetime.datetime.now()) + "\n")
        else:
            del lines[save]  # Deleting outdated query
            overwrite_dict = {
                save: {
                    "query": query_build(
                        name, wires, br, length, start, end, output
                    ),
                    "date": str(datetime.datetime.now()),
                }
            }
            lines.update(
                overwrite_dict
            )  # Essentially replacing the old query with the new dict
            savefile.truncate(0)
            yaml.dump(
                lines, savefile, sort_keys=False, width=float("inf")
            )  # Dumping the overwritten query to the file, forcing no inline output


def query_build(name, wires, br, length, start, end, output):
    """
    Constructing the query using conditionals
    """
    cmd = ""
    if name:
        cmd += f' -f "{name}"'
    if wires:
        cmd += f' -w "{wires}"'
    if br:
        cmd += f' -b "{br}"'
    if length:
        cmd += f' -l "{length}"'
    if start:
        cmd += f' -s "{start}"'
    if end:
        cmd += f' -e "{end}"'
    if output:
        cmd += f" -o"
    return cmd


def is_save_file(filename):
    return os.path.isfile(filename)
