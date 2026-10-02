"""Optional command-line demo matching the VEDA task's menu-driven requirement."""

def calculate(marks):
    total = sum(marks)
    percentage = total / len(marks)
    if percentage >= 90: grade = "A+"
    elif percentage >= 80: grade = "A"
    elif percentage >= 70: grade = "B+"
    elif percentage >= 60: grade = "B"
    elif percentage >= 50: grade = "C"
    elif percentage >= 40: grade = "D"
    else: grade = "F"
    return total, percentage, grade


def main():
    print("\nGradeFlow CLI Demo")
    print("1. Calculate result")
    print("2. Exit")
    choice = input("Choose: ").strip()
    if choice == "1":
        marks = [int(input(f"Subject {i} marks (0-100): ")) for i in range(1, 6)]
        if any(m < 0 or m > 100 for m in marks):
            print("Marks must be between 0 and 100.")
            return
        total, percentage, grade = calculate(marks)
        print(f"Total: {total}/500 | Percentage: {percentage:.2f}% | Grade: {grade}")
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
