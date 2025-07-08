# Aeon's End - Automatic Supply Configuration Tool

This tool automatically generates balanced supply configurations for the cooperative deck-building game **Aeon's End**. Instead of manually selecting which cards to include in your game's market, this application uses the official supply construction rules to create well-balanced 6-card supply combinations that ensure engaging and strategic gameplay.

## What This Tool Does

**Aeon's End** requires players to select 6 different supply cards (the market) before each game begins. Creating a balanced supply manually can be time-consuming and may result in unbalanced gameplay. This tool solves that problem by:

- **Automatically generating supply configurations** based on the official supply construction patterns (6 different rule-based patterns)
- **Ensuring card cost distribution** follows recommended guidelines for balanced gameplay
- **Including specific card abilities** when requested (such as card destruction, breach focusing, charge generation, etc.)
- **Supporting multiple card sets** from different waves of Aeon's End expansions

## Key Features

### Smart Supply Generation
The tool uses predefined patterns that specify:
- Card types (spells, gems, relics)
- Cost ranges for each slot
- Balanced distribution across different price points

### Customizable Card Abilities
You can specify which special abilities you want guaranteed in your supply:
- **Card Destruction** - Remove cards from your deck permanently
- **Breach Focusing** - Improve your breach capabilities
- **Charge Generation** - Gain charge tokens for enhanced spells
- **Gravehold Life Recovery** - Heal the shared life pool
- **Life Recovery** - Heal individual player life
- **Card Draw** - Draw additional cards
- **Multiple Target Damage** - Damage multiple enemies simultaneously

### Expansion Support
Choose which card sets to include:
- **All Cards** - Use the complete card pool
- **1st Wave** - Original sets only
- **2nd Wave** - Newer expansion content

## How to Use

### Online Access
The easiest way to use this tool is through the hosted Streamlit application:

**🌐 [Launch the Tool](https://aeonsendsupplypicker-mhl34eaubsaec6w3aobtvz.streamlit.app/)**

### Local Installation

If you prefer to run the tool locally on your computer:

#### Prerequisites
- Python 3.7 or higher
- The Aeon's End card database (`Aeons_end.db` file)

#### Setup Steps

1. **Clone or download this repository** to your computer

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the database file** `Aeons_end.db` is in the same directory as `main.py`

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

5. **Open your web browser** and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

## Using the Interface

### Step 1: Select Your Card Set
Choose which cards to include in the generation pool:
- **All** - Uses cards from all available expansions
- **1st Wave** - Limited to original card sets
- **2nd Wave** - Uses newer expansion cards

### Step 2: Choose Desired Abilities (Optional)
Check any abilities you want guaranteed in your supply. The tool will ensure at least one card with each selected ability appears in the final configuration, provided it fits within the cost and type constraints of the selected pattern.

### Step 3: Generate Your Supply
Click the **"サプライ選択" (Supply Selection)** button to generate a new supply configuration. The tool will:
1. Randomly select one of the 6 official supply construction patterns
2. Fill each slot according to the pattern's specifications
3. Replace cards as needed to include your requested abilities
4. Display the final 6-card configuration

### Understanding the Results
The generated supply will show:
- **Card names** with their expansion set
- **Supply pattern number** (1-6) that was used
- **Balanced cost distribution** according to official guidelines

## Technical Details

### How Pattern Selection Works
The tool maintains 6 different supply construction patterns in the database, each specifying:
- Card types for each of the 6 slots
- Cost requirements (exact values, ranges, minimums, or maximums)
- Conditions for valid card selection

### Ability Inclusion Logic
When you request specific abilities:
1. The tool first generates a basic supply using the selected pattern
2. It then searches for cards with your requested abilities that fit the pattern constraints
3. It randomly replaces existing cards with ability-matching cards where possible
4. Cards are never replaced if no suitable alternative exists within the pattern constraints

### Database Structure
The application relies on an SQLite database containing:
- **Card information** (names, costs, types, abilities, expansion sets)
- **Supply patterns** (the 6 official construction templates)
- **Ability flags** for efficient filtering

## Dependencies

- **Streamlit** - Web application framework for the user interface
- **Pandas** - Data manipulation and analysis for database operations
- **SQLite3** - Database connectivity (included with Python)

## Troubleshooting

### "該当するカードが存在しません" Error
This error means no cards match the current pattern requirements. This can happen when:
- The selected card set is too restrictive
- The combination of requested abilities and pattern constraints is impossible
- The database is missing expected cards

**Solution:** Try clicking the supply selection button again to get a different pattern, or reduce the number of requested abilities.

### Missing Database File
If you see database connection errors:
- Ensure `Aeons_end.db` is in the same directory as `main.py`
- Verify the database file isn't corrupted
- Check file permissions allow read access

## Contributing

This tool is designed to make Aeon's End setup faster and more enjoyable. If you encounter issues or have suggestions for improvements, please consider contributing to the project.

---

*This tool is a fan-made utility for Aeon's End and is not officially affiliated with Action Phase Games or the game's publishers.*
