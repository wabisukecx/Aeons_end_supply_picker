import json
import streamlit as st
import random
from enum import Enum
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging
from pathlib import Path

# ロギング設定（エラーのみ表示）
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 定数定義
class CardAbility(Enum):
    """カード能力の列挙型"""
    DESTROY_CARD = ("destroy_card", "カード破棄")
    FOCUS_BREACH = ("focus_breach", "破孔強化")
    GAIN_CHARGE = ("gain_charge", "チャージを得る")
    GAIN_GRAVEHOLD_LIFE = ("gain_gravehold_life", "グレイヴホールド回復")
    GAIN_LIFE = ("gain_life", "体力回復")
    DRAW_CARD = ("draw_card", "カードドロー")
    MULTIPLE_DAMAGE = ("multiple_damage", "複数対象ダメージ")
    PULSE_TOKEN = ("pulse_token", "パルストークン")
    SILENT_TOKEN = ("silent_token", "沈静化トークン")
    
    def __init__(self, db_column: str, display_name: str):
        self.db_column = db_column
        self.display_name = display_name

class CardSet(Enum):
    """カードセットの列挙型"""
    ALL = ("all", "全てのカード")
    BASIC_SET = ("基本セット", "基本セット")
    DEPTHS = ("深層", "深層")
    NAMELESS = ("名なき者", "名なき者")
    WAR_ETERNAL = ("終わりなき戦い", "終わりなき戦い")
    VOID = ("虚空", "虚空")
    OUTER_DARK = ("外より来たりし闇", "外より来たりし闇")
    LEGACY = ("レガシー", "レガシー")
    BURIED_SECRETS = ("埋もれた秘密", "埋もれた秘密")
    NEW_AGE = ("新たな時代", "新たな時代")
    OUTCASTS = ("追放されしもの", "追放されしもの")
    
    def __init__(self, value: str, display_name: str):
        self._value_ = value
        self.display_name = display_name

@dataclass
class Card:
    """カード情報を表すデータクラス"""
    name: str
    card_set: str
    type: str
    cost: int
    abilities: Dict[str, bool]
    
    def __str__(self):
        return f"{self.name}（{self.card_set}）"
    
    def has_ability(self, ability: CardAbility) -> bool:
        """特定の能力を持っているかチェック"""
        return self.abilities.get(ability.db_column) == "applicable"

@dataclass
class SupplyComposition:
    """サプライ構成を表すデータクラス"""
    composition: int  # サプライ構成番号
    type: str  # カード種類（宝石、遺物、呪文）
    cost_1: Optional[int]  # エーテル値1（任意の場合はNone）
    cost_2: Optional[int]  # エーテル値2（範囲指定時のみ）
    condition: str  # 条件（以上、以下、等しい、任意）

@dataclass
class NemesisCard:
    """ネメシスカード情報を表すデータクラス"""
    name: str
    type: str
    tier: int
    card_set: str  # カードセット名（必須）
    hp: Optional[int] = None  # ミニオンの場合のみ
    
    def __str__(self):
        if self.type == "ミニオン" and self.hp:
            return f"{self.name} (HP: {self.hp})"
        return self.name

class JSONDataManager:
    """JSONファイルからのデータ管理クラス"""
    
    def __init__(self, 
                 cardlist_path: str = "cardlist.json", 
                 nemesis_basic_path: str = "nemesis_basic_cards.json"):
        self.cardlist_path = Path(cardlist_path)
        self.nemesis_basic_path = Path(nemesis_basic_path)
        
        self.cards: List[Card] = []
        self.nemesis_basic_cards: List[NemesisCard] = []
        
        # 6種類のサプライ構成をコード内に定義
        self.supply_compositions = [
            # サプライ構成1
            SupplyComposition(1, "宝石", 3, None, "以下"),
            SupplyComposition(1, "宝石", 4, None, "等しい"),
            SupplyComposition(1, "宝石", None, None, "任意"),
            SupplyComposition(1, "遺物", None, None, "任意"),
            SupplyComposition(1, "遺物", None, None, "任意"),
            SupplyComposition(1, "呪文", 4, None, "以下"),
            SupplyComposition(1, "呪文", 4, None, "以下"),
            SupplyComposition(1, "呪文", 6, None, "以上"),
            SupplyComposition(1, "呪文", 6, None, "以上"),

            # サプライ構成2
            SupplyComposition(2, "宝石", 4, None, "以上"),
            SupplyComposition(2, "宝石", 4, None, "以上"),
            SupplyComposition(2, "宝石", 4, None, "以上"),
            SupplyComposition(2, "遺物", 5, None, "以上"),
            SupplyComposition(2, "遺物", None, None, "任意"),
            SupplyComposition(2, "呪文", 5, None, "以下"),
            SupplyComposition(2, "呪文", 5, None, "以下"),
            SupplyComposition(2, "呪文", 5, None, "以下"),
            SupplyComposition(2, "呪文", 7, None, "以上"),
            
            # サプライ構成3
            SupplyComposition(3, "宝石", 3, None, "以下"),
            SupplyComposition(3, "宝石", 4, 5, "以下"),
            SupplyComposition(3, "宝石", 4, 5, "以下"),
            SupplyComposition(3, "遺物", None, None, "任意"),
            SupplyComposition(3, "呪文", 3, None, "等しい"),
            SupplyComposition(3, "呪文", 4, None, "等しい"),
            SupplyComposition(3, "呪文", 6, None, "以上"),
            SupplyComposition(3, "呪文", 6, None, "以上"),
            SupplyComposition(3, "呪文", 6, None, "以上"),
            
            # サプライ構成4
            SupplyComposition(4, "宝石", 5, None, "以上"),
            SupplyComposition(4, "宝石", None, None, "任意"),
            SupplyComposition(4, "宝石", None, None, "任意"),
            SupplyComposition(4, "遺物", 3, None, "以下"),
            SupplyComposition(4, "遺物", 5, None, "以上"),
            SupplyComposition(4, "遺物", None, None, "任意"),
            SupplyComposition(4, "呪文", 4, None, "以下"),
            SupplyComposition(4, "呪文", 6, None, "以上"),
            SupplyComposition(4, "呪文", None, None, "任意"),
            
            # サプライ構成5（任意条件の例を含む）
            SupplyComposition(5, "宝石", 2, None, "等しい"),
            SupplyComposition(5, "宝石", 3, None, "等しい"),
            SupplyComposition(5, "宝石", 4, None, "等しい"),
            SupplyComposition(5, "宝石", 5, None, "等しい"),
            SupplyComposition(5, "遺物", None, None, "任意"),
            SupplyComposition(5, "呪文", 4, None, "等しい"),
            SupplyComposition(5, "呪文", 5, None, "等しい"),
            SupplyComposition(5, "呪文", 6, None, "等しい"),
            SupplyComposition(5, "呪文", 7, None, "以上"),
            
            # サプライ構成6
            SupplyComposition(6, "宝石", 3, None, "等しい"),
            SupplyComposition(6, "宝石", 4, None, "等しい"),
            SupplyComposition(6, "遺物", 3, None, "以下"),
            SupplyComposition(6, "遺物", 5, None, "以上"),
            SupplyComposition(6, "遺物", None, None, "任意"),
            SupplyComposition(6, "呪文", 3, 4, "以下"),
            SupplyComposition(6, "呪文", 5, 6, "以下"),
            SupplyComposition(6, "呪文", 5, 6, "以下"),
            SupplyComposition(6, "呪文", 7, None, "以上"),
        ]
        
        self._load_data()
        
    def _load_data(self):
        """JSONファイルからデータを読み込み"""
        try:
            # カードリストの読み込み
            if self.cardlist_path.exists():
                with open(self.cardlist_path, 'r', encoding='utf-8') as f:
                    cardlist_data = json.load(f)
                    
                for card_data in cardlist_data:
                    abilities = {
                        'destroy_card': card_data.get('destroy_card'),
                        'draw_card': card_data.get('draw_card'),
                        'focus_breach': card_data.get('focus_breach'),
                        'gain_charge': card_data.get('gain_charge'),
                        'gain_gravehold_life': card_data.get('gain_gravehold_life'),
                        'gain_life': card_data.get('gain_life'),
                        'multiple_damage': card_data.get('multiple_damage'),
                        'pulse_token': card_data.get('pulse_token'),
                        'silent_token': card_data.get('silent_token')
                    }
                    
                    card = Card(
                        name=card_data['name'],
                        card_set=card_data['card_set'],
                        type=card_data['type'],
                        cost=card_data['cost'],
                        abilities=abilities
                    )
                    self.cards.append(card)
                    
                logger.info(f"カードリスト読み込み完了: {len(self.cards)}枚")
            else:
                logger.warning(f"{self.cardlist_path} が見つかりません")
                
            # ネメシス基本カードの読み込み
            if self.nemesis_basic_path.exists():
                with open(self.nemesis_basic_path, 'r', encoding='utf-8') as f:
                    nemesis_basic_data = json.load(f)
                    
                for card_data in nemesis_basic_data:
                    card = NemesisCard(
                        name=card_data['name'],
                        type=card_data['type'],
                        tier=card_data['tier'],
                        card_set=card_data['card_set'],
                        hp=card_data.get('hp')
                    )
                    self.nemesis_basic_cards.append(card)
                    
                logger.info(f"ネメシス基本カード読み込み完了: {len(self.nemesis_basic_cards)}種類")
            else:
                logger.warning(f"{self.nemesis_basic_path} が見つかりません")
                
            # デフォルトルールを設定（要求書に記載されているデフォルト値）
            self.player_count_rules = {
                "1": {"tier_1": 1, "tier_2": 3, "tier_3": 7, "note": "1人プレイ用の配分"},
                "2": {"tier_1": 3, "tier_2": 5, "tier_3": 7, "note": "2人プレイ用の配分"},
                "3": {"tier_1": 5, "tier_2": 6, "tier_3": 7, "note": "3人プレイ用の配分"},
                "4": {"tier_1": 8, "tier_2": 7, "tier_3": 7, "note": "4人プレイ用の配分"}
            }
        except Exception as e:
            logger.error(f"データ読み込みエラー: {e}")
            raise
            
    def get_composition(self, composition_id: int) -> List[SupplyComposition]:
        """指定されたサプライ構成IDのサプライ構成を取得"""
        return [c for c in self.supply_compositions if c.composition == composition_id]
        
    def search_cards(self, card_type: str, cost_condition: Dict,
                    card_sets: List[CardSet], ability: Optional[CardAbility] = None,
                    exclude_cards: List[str] = None) -> List[Card]:
        """条件に合うカードを検索"""
        try:
            # 基本フィルタリング
            filtered_cards = [c for c in self.cards if c.type == card_type]
            
            # エーテル値（コスト）条件でフィルタリング
            if cost_condition.get('condition') == '任意':
                # 任意の場合はコスト制限なし
                pass
            elif 'between' in cost_condition:
                filtered_cards = [
                    c for c in filtered_cards 
                    if cost_condition['cost1'] <= c.cost <= cost_condition['cost2']
                ]
            elif 'condition' in cost_condition:
                if cost_condition['condition'] == '以下':
                    filtered_cards = [
                        c for c in filtered_cards 
                        if c.cost <= cost_condition['cost']
                    ]
                elif cost_condition['condition'] == '以上':
                    filtered_cards = [
                        c for c in filtered_cards 
                        if c.cost >= cost_condition['cost']
                    ]
                elif cost_condition['condition'] == '等しい':
                    filtered_cards = [
                        c for c in filtered_cards 
                        if c.cost == cost_condition['cost']
                    ]
                    
            # カードセットでフィルタリング（複数選択対応）
            if CardSet.ALL not in card_sets:
                card_set_values = [cs.value for cs in card_sets]
                filtered_cards = [
                    c for c in filtered_cards 
                    if c.card_set in card_set_values
                ]
                
            # 能力でフィルタリング
            if ability:
                filtered_cards = [
                    c for c in filtered_cards 
                    if c.has_ability(ability)
                ]
                
            # 除外カードをフィルタリング
            if exclude_cards:
                exclude_names = [card.split('（')[0] for card in exclude_cards]
                filtered_cards = [
                    c for c in filtered_cards 
                    if c.name not in exclude_names
                ]
                
            return filtered_cards
            
        except Exception as e:
            logger.error(f"カード検索エラー: {e}")
            return []
    
    def get_nemesis_basic_cards(self, card_sets: List[str]) -> List[NemesisCard]:
        """指定されたカードセットの基本カードを取得"""
        if "all" in card_sets:
            return self.nemesis_basic_cards
        return [card for card in self.nemesis_basic_cards if card.card_set in card_sets]

class SupplyGenerator:
    """サプライ生成ロジックを管理するクラス"""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        
    def generate_supply(self, card_sets: List[CardSet],
                       required_abilities: List[CardAbility]) -> Tuple[List[Card], int]:
        """サプライカードを生成（6種類の公式パターンからランダム選択）"""
        # ランダムにパターンを選択（要求書で言及されている6種類の公式パターン）
        pattern_id = random.randint(1, 6)
        compositions = self.data_manager.get_composition(pattern_id)
        
        if not compositions:
            raise ValueError(f"パターン{pattern_id}の取得に失敗しました")
            
        # 基本のサプライを生成
        supply_cards = self._generate_basic_supply(compositions, card_sets)
        
        # 必要な能力を持つカードに置き換え
        supply_cards = self._apply_required_abilities(
            supply_cards, compositions, card_sets, required_abilities
        )
        
        return supply_cards, pattern_id
        
    def _generate_basic_supply(self, compositions: List[SupplyComposition],
                              card_sets: List[CardSet]) -> List[Card]:
        """基本のサプライを生成"""
        supply_cards = []
        
        for composition in compositions:
            cost_condition = self._parse_cost_condition(composition)
            cards = self.data_manager.search_cards(
                card_type=composition.type,
                cost_condition=cost_condition,
                card_sets=card_sets,
                exclude_cards=[str(card) for card in supply_cards]
            )
            
            if cards:
                supply_cards.append(random.choice(cards))
            else:
                logger.warning(
                    f"サプライ構成{composition.composition}のスロット"
                    f"（{composition.type}、エーテル値条件: {cost_condition}）"
                    f"に該当するカードが見つかりません"
                )
                
        return supply_cards
        
    def _apply_required_abilities(self, supply_cards: List[Card],
                                 compositions: List[SupplyComposition], card_sets: List[CardSet],
                                 required_abilities: List[CardAbility]) -> List[Card]:
        """必要な能力を持つカードに置き換え"""
        if not required_abilities:
            return supply_cards
            
        for ability in required_abilities:
            # 既にその能力を持つカードがあるかチェック
            existing_cards_with_ability = [card for card in supply_cards if card.has_ability(ability)]
            if existing_cards_with_ability:
                continue
                
            # 置き換え可能なスロットを探す
            replaceable_slots = []
            replacement_candidates = []
            
            for i, composition in enumerate(compositions):
                if i < len(supply_cards):  # 既存のカードがある場合のみ
                    cost_condition = self._parse_cost_condition(composition)
                    cards = self.data_manager.search_cards(
                        card_type=composition.type,
                        cost_condition=cost_condition,
                        card_sets=card_sets,
                        ability=ability,
                        exclude_cards=[str(card) for card in supply_cards]
                    )
                    
                    if cards:
                        replaceable_slots.append(i)
                        replacement_candidates.append(cards)
                        
            # ランダムに1つのスロットを選んで置き換え
            if replaceable_slots:
                slot_index = random.randint(0, len(replaceable_slots) - 1)
                slot = replaceable_slots[slot_index]
                replacement = random.choice(replacement_candidates[slot_index])
                supply_cards[slot] = replacement
                logger.info(f"{ability.display_name}を持つ{replacement.name}に置き換えました")
                
        return supply_cards
        
    def _parse_cost_condition(self, composition: SupplyComposition) -> Dict:
        """エーテル値条件をパース"""
        if composition.condition == '任意':
            return {'condition': '任意'}
        elif composition.cost_2 is not None:
            return {
                'between': True,
                'cost1': composition.cost_1,
                'cost2': composition.cost_2
            }
        else:
            return {
                'condition': composition.condition,
                'cost': composition.cost_1
            }

class NemesisDeckGenerator:
    """ネメシス基本カード生成ロジックを管理するクラス"""
    
    def __init__(self, data_manager: JSONDataManager):
        self.data_manager = data_manager
        
    def generate_basic_cards_only(self, card_sets: List[str], player_count: int) -> Tuple[List[NemesisCard], Dict[int, int]]:
        """ネメシス基本カードのみを生成（プレイヤー人数に応じた基本カード枚数の自動設定）
        
        Args:
            card_sets: 選択されたカードセットのリスト（["all"], ["基本セット", "深層"], etc.）
            player_count: プレイヤー人数
        
        Returns:
            (生成された基本カードデッキ, 使用したティア配分)
        """
        basic_deck = []
        
        # プレイヤー人数に基づいてティア配分を取得
        player_count_str = str(player_count)
        if player_count_str not in self.data_manager.player_count_rules:
            raise ValueError(f"プレイヤー人数 {player_count} は対応していません")
            
        tier_rules = self.data_manager.player_count_rules[player_count_str]
        tier_distribution = {
            1: tier_rules["tier_1"],
            2: tier_rules["tier_2"],
            3: tier_rules["tier_3"]
        }
        
        # 指定されたカードセットの基本カードを取得
        basic_cards = self.data_manager.get_nemesis_basic_cards(card_sets)
        
        for tier, count in tier_distribution.items():
            tier_cards = [card for card in basic_cards if card.tier == tier]
            
            # 指定された枚数になるまでカードを選択
            selected_cards = []
            while len(selected_cards) < count and tier_cards:
                # ランダムに選択（各カードは1回ずつ選択）
                available_cards = [card for card in tier_cards if card not in selected_cards]
                
                if available_cards:
                    selected_card = random.choice(available_cards)
                    selected_cards.append(selected_card)
                else:
                    logger.warning(f"ティア{tier}の基本カードが不足しています")
                    break
            
            basic_deck.extend(selected_cards)
        
        # 基本カードデッキをシャッフル
        random.shuffle(basic_deck)
        
        return basic_deck, tier_distribution

def create_ui():
    """Streamlit UIを作成"""
    st.set_page_config(
        page_title="イーオンズ・エンド - 自動サプライ生成",
        page_icon="🔮",
        layout="wide"
    )
    
    st.title('🔮 イーオンズ・エンド - 自動サプライ生成')
    st.markdown("---")
    
    # セッション状態の初期化
    if 'supply_history' not in st.session_state:
        st.session_state.supply_history = []
    if 'nemesis_deck_history' not in st.session_state:
        st.session_state.nemesis_deck_history = []
    
    # データマネージャーの初期化
    try:
        data_manager = JSONDataManager()
    except FileNotFoundError as e:
        st.error(f"必要なJSONファイルが見つかりません: {str(e)}")
        st.info("必要なファイル: cardlist.json, nemesis_basic_cards.json")
        st.stop()
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        st.stop()
    
    # タブの作成
    tab1, tab2 = st.tabs(["🎯 サプライ生成", "👹 ネメシス基本カード生成"])
    
    # サプライ生成タブ
    with tab1:
        # スマホ向け：縦配置レイアウト
        st.header("⚙️ サプライ設定")
        
        # カードセット選択（複数選択対応）
        st.markdown("### 📦 カードセット選択")
        st.caption("含めたいカードセットを選択（複数選択可能）")
        
        card_sets_selected = []
        for card_set in CardSet:
            if st.checkbox(card_set.display_name, key=f"supply_cardset_{card_set.name}", 
                          value=(card_set == CardSet.BASIC_SET)):
                card_sets_selected.append(card_set)
        
        if not card_sets_selected:
            card_sets_selected = [CardSet.ALL]
        
        st.markdown("### 🎯 必要な能力")
        st.caption("含めたい能力を選択（選択した能力を持つカードが優先的に含まれます）")
        
        # 能力選択
        abilities_selected = []
        abilities_list = list(CardAbility)
        
        for ability in abilities_list:
            if st.checkbox(ability.display_name, key=f"supply_{ability.name}"):
                abilities_selected.append(ability)
        
        # サプライ生成ボタン
        if st.button('🎲 サプライ生成', use_container_width=True, type="primary", key="generate_supply"):
            try:
                generator = SupplyGenerator(data_manager)
                supply_cards, composition_id = generator.generate_supply(
                    card_sets_selected, abilities_selected
                )
                
                if len(supply_cards) < 9:
                    st.warning(
                        f"⚠️ 条件に合うカードが不足しています。"
                        f"{len(supply_cards)}枚のみ生成されました。"
                    )
                
                # 履歴に追加
                st.session_state.supply_history.insert(0, {
                    'cards': supply_cards,
                    'composition': composition_id,
                    'abilities': [a.display_name for a in abilities_selected],
                    'card_sets': [cs.display_name for cs in card_sets_selected]
                })
                
                # 最新の10件のみ保持
                st.session_state.supply_history = st.session_state.supply_history[:10]
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
                logger.error(f"サプライ生成エラー: {e}", exc_info=True)
        
        # サプライ結果表示（縦配置）
        if st.session_state.supply_history:
            st.markdown("---")
            latest = st.session_state.supply_history[0]
            
            st.markdown("### 🔮 生成されたサプライ")
            
            # サプライ構成情報と設定表示
            st.info(f"**6種類のサプライ構成 {latest['composition']}** を使用")
            if latest['card_sets'] and latest['card_sets'] != ['全てのカード']:
                st.info(f"**使用カードセット**: {', '.join(latest['card_sets'])}")
            
            # カード表示（スマホ向け：3×3のグリッド）
            for row in range(3):
                cols = st.columns(3)
                for col_idx in range(3):
                    card_idx = row * 3 + col_idx
                    if card_idx < len(latest['cards']):
                        card = latest['cards'][card_idx]
                        with cols[col_idx]:
                            # カード情報ボックス（カード名、wave、カード種別のみ）
                            with st.container():
                                st.markdown(f"**{card_idx + 1}. {card.name}**")
                                
                                # カード種別とWave（縦に配置）
                                type_color = {"宝石": "🔵", "遺物": "🟡", "呪文": "🔴"}.get(card.type, "⚫")
                                st.markdown(f"{type_color} {card.type}")
                                st.caption(f"📦 {card.card_set}")  # card_setを表示
                                
                                # カードの能力を表示（要求された能力がある場合のみ）
                                if latest['abilities']:
                                    card_abilities = []
                                    for ability in CardAbility:
                                        if card.has_ability(ability):
                                            card_abilities.append(ability.display_name)
                                    if card_abilities:
                                        st.caption(f"🎯 {', '.join(card_abilities)}")
                                    else:
                                        st.caption("🎯 ―")  # 能力がない場合も行を表示
                                
                                st.markdown("---")
    
    # ネメシス基本カード生成タブ
    with tab2:
        st.header("⚙️ ネメシス基本カード設定")
        
        # プレイヤー人数選択
        player_count = st.selectbox(
            '👥 プレイヤー人数：',
            options=[1, 2, 3, 4],
            index=1,  # デフォルトは2人
            key="player_count"
        )
        
        # カードセット選択（複数選択対応）
        st.markdown("### 📦 ネメシス基本カード カードセット選択")
        st.caption("含めたいカードセットを選択（複数選択可能）")
        
        nemesis_card_sets_selected = []
        for card_set in CardSet:
            if st.checkbox(card_set.display_name, key=f"nemesis_cardset_{card_set.name}", 
                          value=(card_set == CardSet.BASIC_SET)):
                nemesis_card_sets_selected.append(card_set)
        
        if not nemesis_card_sets_selected:
            nemesis_card_sets_selected = [CardSet.ALL]
        
        # ネメシス基本カード生成ボタン
        if st.button('👹 ネメシス基本カード生成', use_container_width=True, type="primary", key="generate_nemesis_deck"):
            try:
                generator = NemesisDeckGenerator(data_manager)
                
                # 選択されたカードセットの値を取得
                card_set_values = [cs.value for cs in nemesis_card_sets_selected]
                
                basic_deck, tier_distribution = generator.generate_basic_cards_only(card_set_values, player_count)
                
                # 履歴に追加
                st.session_state.nemesis_deck_history.insert(0, {
                    'basic_deck': basic_deck,
                    'tier_distribution': tier_distribution,
                    'player_count': player_count,
                    'card_sets': [cs.display_name for cs in nemesis_card_sets_selected]
                })
                
                # 最新の5件のみ保持
                st.session_state.nemesis_deck_history = st.session_state.nemesis_deck_history[:5]
                
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}")
                logger.error(f"ネメシス基本カード生成エラー: {e}", exc_info=True)
        
        # ネメシス基本カード結果表示
        if st.session_state.nemesis_deck_history:
            st.markdown("---")
            latest = st.session_state.nemesis_deck_history[0]
            
            st.markdown(f"### 👹 ネメシス基本カードデッキ")
            
            # Tier別でグループ化
            cards_by_tier = {1: [], 2: [], 3: []}
            for card in latest['basic_deck']:
                cards_by_tier[card.tier].append((card.name, card.type, card.card_set))
            
            # Tier別に表示
            for tier in [1, 2, 3]:
                cards_info = cards_by_tier[tier]
                if cards_info:
                    st.markdown(f"**ティア{tier} ({len(cards_info)}枚)**")
                    for name, card_type, card_set in cards_info:
                        # カード種別アイコン
                        type_icon = {"アタック": "⚔️", "パワー": "💪", "ミニオン": "👹"}.get(card_type, "🔮")
                        st.markdown(f"• {type_icon} {name} ({card_set})")
                    st.markdown("")

def main():
    """メイン関数"""
    create_ui()

if __name__ == '__main__':
    main()
