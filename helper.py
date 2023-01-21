class Helper:
    def __init__(self, seperator_counter=0, order_counter=51):
        self.seperator_counter = seperator_counter
        self.order_counter = order_counter

    def order(self) -> int:
        self.order_counter += 1
        return self.order_counter

    def seperator(self) -> str:
        self.seperator_counter += 1
        return (f'{T(4)}seperator_{self.seperator_counter} = {{\n'
                f'{T(5)}type = "header",\n'
                f'{T(5)}name = "",\n'
                f'{T(5)}order = {self.order()},\n'
                f'{T(4)}}},\n')


def T(count: int) -> str:
    return "\t" * count


def N(count: int = 1) -> str:
    return "\n" * count


def color_setgets(color_name: str) -> str:
    return (f'{T(5)}get = function()\n'
            f'{T(6)}local color = self.db.profile.color.{color_name}\n'
            f'{T(6)}AdiBags:UpdateFilters()\n'
            f'{T(6)}return color.r, color.g, color.b\n'
            f'{T(5)}end,\n'

            f'{T(5)}set = function(_, r, g, b)\n'
            f'{T(6)}local color = self.db.profile.color.{color_name}\n'
            f'{T(6)}color.r, color.g, color.b = r, g, b\n'
            f'{T(6)}AdiBags:UpdateFilters()\n'
            f'{T(5)}end,\n')
