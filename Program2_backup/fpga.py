class LUT4:
    def __init__(self, sram_values):
        if len(sram_values) != 16:
            raise ValueError("SRAM must have exactly 16 values.")
        self.sram = sram_values

    def compute(self, inputs):
        if len(inputs) != 4:
            raise ValueError("LUT4 requires exactly 4 input values.")
        input_index = int("".join(['1' if i else '0' for i in inputs]), 2)
        return self.sram[input_index]


sram_values = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0]
lut0 = LUT4(sram_values)

###
output = lut0.compute([1, 1, 1, 0])
print(output)
###

class Crossbar:
    """
    A simple model of a crossbar switch with configurable inputs and outputs.
    """
    def __init__(self, num_inputs, num_outputs):
        """
        Initialize the crossbar with a given number of inputs and outputs.
        :param num_inputs: Number of input lines.
        :param num_outputs: Number of output lines.
        """
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        # Initialize the switch matrix with all connections set to False
        self.switch_matrix = [[False for _ in range(num_outputs)] for _ in range(num_inputs)]

    def connect(self, input_index, output_index):
        """
        Create a connection between an input and an output.
        :param input_index: Index of the input line.
        :param output_index: Index of the output line.
        """
        self.switch_matrix[input_index][output_index] = True

    def disconnect(self, input_index, output_index):
        """
        Remove a connection between an input and an output.
        :param input_index: Index of the input line.
        :param output_index: Index of the output line.
        """
        self.switch_matrix[input_index][output_index] = False

    def is_connected(self, input_index, output_index):
        """
        Check if a specific input is connected to a specific output.
        :param input_index: Index of the input line.
        :param output_index: Index of the output line.
        :return: True if connected, False otherwise.
        """
        return self.switch_matrix[input_index][output_index]


# Example usage of the Crossbar
crossbar = Crossbar(4, 4)  # 4 inputs and 4 outputs

# Connect some inputs to outputs
crossbar.connect(0, 2)
crossbar.connect(1, 3)
crossbar.connect(2, 1)
crossbar.connect(3, 0)

# Check if a specific connection exists
connection_status = crossbar.is_connected(0, 2)  # Checking if input 0 is connected to output 2
connection_status
