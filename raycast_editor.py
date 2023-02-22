from editor import Editor

if __name__ == "__main__":
    editor = Editor()
    editor.load_world("maze.map")
    editor.run()