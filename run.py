import arcade
import config
from visualization import App


def main():
    app = App()
    app.setup()

    arcade.run()


if __name__ == '__main__':
    main()
