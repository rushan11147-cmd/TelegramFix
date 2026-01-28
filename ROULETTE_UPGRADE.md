# 🎰 Улучшение рулетки с барабаном

## Что добавить в templates/simple.html:

### 1. Найди модальное окно рулетки (строка ~638):
```html
<div class="modal" id="rouletteModal">
```

### 2. Замени весь блок `<div class="modal-body">` на:

```html
<div class="modal-body" style="text-align: center;">
    <!-- Барабан рулетки -->
    <div style="background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 20px; padding: 30px; margin: 20px 0; border: 4px solid #f39c12; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <div style="background: #1a252f; border-radius: 15px; padding: 20px; overflow: hidden; position: relative;">
            <!-- Барабаны -->
            <div style="display: flex; gap: 10px; justify-content: center; align-items: center; height: 100px;">
                <div class="roulette-slot" id="slot1">🎰</div>
                <div class="roulette-slot" id="slot2">🎰</div>
                <div class="roulette-slot" id="slot3">🎰</div>
            </div>
            <!-- Линия результата -->
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100%; height: 2px; background: #f39c12; pointer-events: none;"></div>
        </div>
        <div style="font-size: 24px; margin-top: 15px; color: #f39c12; font-weight: bold;" id="rouletteMessage">Поставь деньги и крути!</div>
    </div>
    
    <div style="display: flex; gap: 10px; justify-content: center; margin: 20px 0;">
        <button class="nav-btn" style="padding: 15px 20px; background: linear-gradient(135deg, #27ae60 0%, #229954 100%); border-color: #1e8449;" onclick="spinRoulette(100)">
            <div style="font-size: 18px; font-weight: bold;">100₽</div>
        </button>
        <button class="nav-btn" style="padding: 15px 20px; background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-color: #21618c;" onclick="spinRoulette(500)">
            <div style="font-size: 18px; font-weight: bold;">500₽</div>
        </button>
        <button class="nav-btn" style="padding: 15px 20px; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); border-color: #a93226;" onclick="spinRoulette(1000)">
            <div style="font-size: 18px; font-weight: bold;">1000₽</div>
        </button>
    </div>
    <div style="font-size: 14px; color: #888; margin-top: 10px;">
        Шансы: 60% x0 | 25% x2 | 10% x5 | 5% x10
    </div>
</div>
```

### 3. Добавь CSS стили (в секцию `<style>`):

```css
.roulette-slot {
    font-size: 60px;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
    border-radius: 10px;
    border: 3px solid #f39c12;
    transition: transform 0.1s;
}

@keyframes spin {
    0% { transform: translateY(0); }
    100% { transform: translateY(-500px); }
}

.spinning {
    animation: spin 0.1s linear infinite;
}
```

### 4. Добавь JavaScript функцию (в секцию `<script>`):

```javascript
const rouletteSymbols = ['😭', '🙂', '😄', '🤑', '💰', '🎰', '🎲', '🍀'];
let isSpinning = false;

async function spinRoulette(bet) {
    if (isSpinning) return;
    isSpinning = true;
    
    // Анимация вращения
    const slots = [
        document.getElementById('slot1'),
        document.getElementById('slot2'),
        document.getElementById('slot3')
    ];
    
    document.getElementById('rouletteMessage').textContent = 'Крутим...';
    
    // Быстрое вращение
    let spinCount = 0;
    const spinInterval = setInterval(() => {
        slots.forEach(slot => {
            slot.textContent = rouletteSymbols[Math.floor(Math.random() * rouletteSymbols.length)];
        });
        spinCount++;
        
        if (spinCount > 20) {
            clearInterval(spinInterval);
            // Отправляем запрос на сервер
            playRouletteReal(bet, slots);
        }
    }, 100);
}

async function playRouletteReal(bet, slots) {
    try {
        const response = await fetch('/api/play_roulette', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, bet: bet })
        });
        
        if (response.ok) {
            const data = await response.json();
            gameData = data.user;
            
            // Показываем результат
            const resultEmoji = data.result_emoji;
            slots.forEach(slot => {
                slot.textContent = resultEmoji;
                slot.style.transform = 'scale(1.2)';
                setTimeout(() => slot.style.transform = 'scale(1)', 300);
            });
            
            document.getElementById('rouletteMessage').textContent = data.message;
            
            updateUI();
            showMessage(data.message, data.multiplier > 0);
        } else {
            const error = await response.json();
            showMessage(error.error || 'Ошибка!', false);
            slots.forEach(slot => slot.textContent = '❌');
            document.getElementById('rouletteMessage').textContent = 'Ошибка!';
        }
    } catch (error) {
        showMessage('Ошибка сети!', false);
        slots.forEach(slot => slot.textContent = '❌');
        document.getElementById('rouletteMessage').textContent = 'Ошибка!';
    }
    
    isSpinning = false;
}
```

### 5. Удали старую функцию playRoulette (если есть)

---

## Результат:

✅ Красивый барабан с 3 слотами
✅ Анимация вращения символов
✅ Золотая рамка и темный фон
✅ Линия показывает результат
✅ Увеличение символов при выигрыше
✅ Цветные кнопки ставок

Теперь рулетка выглядит как настоящий слот-автомат! 🎰
