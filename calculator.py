# Calculator module

def calculate_average(numbers):
    if not numbers:
        return 0  # or raise ValueError("Cannot calculate average of an empty list")
    total = sum(numbers)
    return total / len(numbers)

# Example usage:
if __name__ == "__main__":
    print(calculate_average([1, 2, 3]))
    print(calculate_average([]))