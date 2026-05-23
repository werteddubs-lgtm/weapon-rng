import streamlit as st
import random
import json
import base64

# --- INITIALIZATION & DATABASE ---
if 'game_initialized' not in st.session_state:
    st.session_state.rarities = [
        "Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", 
        "Omniscient", "Transcendent", "Merciless", "World Ending", 
        "Challenged", "Challenged +", "Meme", "Shitpost", "Unreal", 
        "Multiversal Collapse", "Author's Blessing", "Absolute Zero"
    ]
    st.session_state.rarity_weights = {
        "Common": 1000.0, "Uncommon": 250.0, "Rare": 60.0, "Epic": 15.0, "Legendary": 3.0,
        "Mythic": 0.5, "Omniscient": 0.08, "Transcendent": 0.015, "Merciless": 0.003,
        "World Ending": 0.0005, "Challenged": 0.00009, "Challenged +": 0.00001,
        "Meme": 0.000002, "Shitpost": 0.0000004, "Unreal": 0.00000007,
        "Multiversal Collapse": 0.00000001, "Author's Blessing": 0.000000002,
        "Absolute Zero": 0.0000000001
    }
    st.session_state.worlds = {
        1: "Bamboo Forest", 2: "Neon Tokyo Underground", 3: "Shadow Dojo", 
        4: "The Void Core", 5: "The Internet Singularity", 6: "Atlantis Ruins", 
        7: "Cyber-Punk Casino", 8: "Valhalla Banquet Hall", 9: "Chrono Nexus", 
        10: "Deep Space Void", 11: "Hyperborea Ice Caverns", 12: "Underworld Gates", 
        13: "Glitch Matrix Arcade", 14: "The Backrooms Level 0", 15: "Developer Sandbox", 
        16: "The Final Dimension", 17: "The AI Core Matrix"
    }
    st.session_state.loot_table = [
        {"name": "Rusty Kunai", "rarity": "Common", "value": 5, "world": 1},
        {"name": "Bamboo Staff", "rarity": "Common", "value": 8, "world": 1},
        {"name": "Steel Tanto", "rarity": "Uncommon", "value": 25, "world": 1},
        {"name": "Shinobi Hood", "rarity": "Rare", "value": 90, "world": 1},
        {"name": "Apprentice Katana", "rarity": "Epic", "value": 300, "world": 1},
        {"name": "Laser Dagger", "rarity": "Uncommon", "value": 110, "world": 2},
        {"name": "Plasma Shield", "rarity": "Rare", "value": 300, "world": 2},
        {"name": "Muramasa Blade", "rarity": "Epic", "value": 800, "world": 2},
        {"name": "Cybernetic RPG", "rarity": "Legendary", "value": 3000, "world": 2},
        {"name": "Nanotech Katana", "rarity": "Mythic", "value": 10000, "world": 2},
        {"name": "Dark Shuriken", "rarity": "Rare", "value": 600, "world": 3},
        {"name": "Oni Cursed Mask", "rarity": "Epic", "value": 2000, "world": 3},
        {"name": "Shadow Blade Katana", "rarity": "Legendary", "value": 7000, "world": 3},
        {"name": "Demonic RPG-7", "rarity": "Mythic", "value": 18000, "world": 3},
        {"name": "Omniscient Eye Charm", "rarity": "Omniscient", "value": 60000, "world": 3},
        {"name": "Transcendent Spirit Saber", "rarity": "Transcendent", "value": 180000, "world": 3},
        {"name": "Void Essence", "rarity": "Mythic", "value": 30000, "world": 4},
        {"name": "Singularity Cannon", "rarity": "Omniscient", "value": 80000, "world": 4},
        {"name": "Cosmic Infused RPG", "rarity": "Transcendent", "value": 300000, "world": 4},
        {"name": "Merciless Executioner Katana", "rarity": "Merciless", "value": 1000000, "world": 4},
        {"name": "World Ending Cataclysm RPG", "rarity": "World Ending", "value": 4500000, "world": 4},
        {"name": "The Challenged Blade", "rarity": "Challenged", "value": 18000000, "world": 4},
        {"name": "Challenged + Hypernova RPG", "rarity": "Challenged +", "value": 75000000, "world": 4},
        {"name": "Glitch Dagger", "rarity": "Transcendent", "value": 500000, "world": 5},
        {"name": "Trollface Mask", "rarity": "Meme", "value": 4206969, "world": 5},
        {"name": "Doge Rocket Launcher", "rarity": "Meme", "value": 6942000, "world": 5},
        {"name": "Rickroll Katana", "rarity": "Meme", "value": 9999999, "world": 5},
        {"name": "Deep-Fried Laser Beam", "rarity": "Shitpost", "value": 15000000, "world": 5},
        {"name": "Comically Large Spoon RPG", "rarity": "Shitpost", "value": 22000000, "world": 5},
        {"name": "Poseidon's Trident", "rarity": "Legendary", "value": 25000, "world": 6},
        {"name": "Reality Eraser Katana", "rarity": "Multiversal Collapse", "value": 90000000000, "world": 16},
        {"name": "Prompt Injection Hypernova", "rarity": "Absolute Zero", "value": 9999999999999, "world": 17}
    ]
    
    # Live Player State Variables
    st.session_state.inventory = {}
    st.session_state.coins = 100
    st.session_state.base_luck = 1.0
    st.session_state.crafted_luck = 0.0
    st.session_state.current_world = 1
    st.session_state.luck_cost = 150
    st.session_state.auto_sell_tier = "None"
    st.session_state.log = ["Welcome to the Infinite RNG Simulator! Ready your luck."]
    st.session_state.game_initialized = True

# --- HELPER FUNCTIONS ---
def get_total_luck():
    return st.session_state.base_luck + st.session_state.crafted_luck

def roll_one():
    world_loot = [i for i in st.session_state.loot_table if i["world"] == st.session_state.current_world]
    if not world_loot:
        return "🎲 No items found in this world zone yet."
    
    available_rarities = list(set(i["rarity"] for i in world_loot))
    pool_weights, pool_items = [], []
    
    for r in available_rarities:
        items_of_rarity = [i for i in world_loot if i["rarity"] == r]
        for item in items_of_rarity:
            weight = st.session_state.rarity_weights[r]
            if r != "Common":
                weight *= (get_total_luck() ** 0.65)
            pool_weights.append(weight)
            pool_items.append(item)
            
    selected = random.choices(pool_items, weights=pool_weights, k=1)[0]
    
    if st.session_state.auto_sell_tier != "None":
        p_idx = st.session_state.rarities.index(selected["rarity"])
        f_idx = st.session_state.rarities.index(st.session_state.auto_sell_tier)
        if p_idx <= f_idx:
            st.session_state.coins += selected["value"]
            return f"🤖 [AUTO-SOLD] [{selected['rarity'].upper()}] {selected['name']} for 💰{selected['value']} coins."
            
    st.session_state.inventory[selected["name"]] = st.session_state.inventory.get(selected["name"], 0) + 1
    return f"🎒 [ACQUIRED] [{selected['rarity'].upper()}] {selected['name']} added to backpack!"

def get_save_code():
    data = {
        "inv": st.session_state.inventory, "coins": st.session_state.coins,
        "bluck": st.session_state.base_luck, "cluck": st.session_state.crafted_luck,
        "world": st.session_state.current_world, "cost": st.session_state.luck_cost
    }
    return base64.b64encode(json.dumps(data).encode()).decode()

def load_save_code(code):
    try:
        data = json.loads(base64.b64decode(code.encode()).decode())
        st.session_state.inventory = data["inv"]
        st.session_state.coins = data["coins"]
        st.session_state.base_luck = data["bluck"]
        st.session_state.crafted_luck = data["cluck"]
        st.session_state.current_world = data["world"]
        st.session_state.luck_cost = data["cost"]
        return True
    except:
        return False

# --- WEB UI DESIGN ---
st.set_page_config(page_title="Infinite RNG RPG", layout="wide")
st.title("💎 Infinite RNG RPG Simulator v3.0")

# Sidebar Configuration (Stats & Controls)
with st.sidebar:
    st.header("👤 Player Statistics")
    st.metric(label="Coins Balance", value=f"💰 {st.session_state.coins:,}")
    st.metric(label="Total Luck Multiplier", value=f"🍀 {get_total_luck():.2f}x")
    st.subheader(f"🌍 {st.session_state.worlds[st.session_state.current_world]}")
    
    st.divider()
    st.header("⚙️ Automation Engine")
    st.session_state.auto_sell_tier = st.selectbox(
        "Auto-Sell Threshold (And Below)", 
        ["None"] + st.session_state.rarities
    )
    
    st.divider()
    st.header("💾 Backup Core")
    save_str = get_save_code()
    st.text_area("Your Cloud Save Code:", value=save_str, height=70, help="Copy this to save progress.")
    load_input = st.text_input("Paste Save Code to Load:")
    if st.button("Execute Data Load"):
        if load_save_code(load_input):
            st.success("Progress restored!")
            st.rerun()
        else:
            st.error("Corrupted save file.")

# Main Action Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🕹️ Control Terminal")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🎲 Single Roll", use_container_width=True):
            res = roll_one()
            st.session_state.log.insert(0, res)
    with col_r2:
        loops = st.number_input("Auto-Roll Count", min_value=1, max_value=20, value=5)
        if st.button(f"🤖 Auto-Roll {loops}x", use_container_width=True):
            for _ in range(loops):
                res = roll_one()
                st.session_state.log.insert(0, res)
    with col_r3:
        if st.button(f"✨ Upgrade Luck (💰{st.session_state.luck_cost:,})", use_container_width=True):
            if st.session_state.coins >= st.session_state.luck_cost:
                st.session_state.coins -= st.session_state.luck_cost
                st.session_state.base_luck *= 1.8
                st.session_state.luck_cost = int(st.session_state.luck_cost * 2.2)
                st.session_state.log.insert(0, "🍀 LUCK MULTIPLIER ASCENDED!")
            else:
                st.error("Insufficient coins!")

    st.divider()
    st.subheader("🌍 Spatial Dimensions")
    world_selection = st.selectbox(
        "Select Travel Destination:", 
        options=list(st.session_state.worlds.keys()), 
        format_func=lambda x: f"World {x}: {st.session_state.worlds[x]}"
    )
    if st.button("Engage Dimensional Jump"):
        st.session_state.current_world = world_selection
        st.session_state.log.insert(0, f"🚀 Teleported to World {world_selection}!")
        st.rerun()

    st.divider()
    st.subheader("📜 Live Feed Log")
