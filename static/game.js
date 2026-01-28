// Игровые данные
let userId = localStorage.getItem('userId') || 'demo_user_' + Math.random().toString(36).substr(2, 9);
let gameData = {};

// Инициализация Telegram WebApp
try {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();
        
        const user = tg.initDataUnsafe?.user;
        if (user && user.id) {
            userId = 'tg_' + user.id.toString();
            localStorage.setItem('userId', userId);
        }
    }
} catch (error) {
    console.log('Telegram WebApp error:', error);
}

// Сохраняем userId если его еще нет
if (!localStorage.getItem('userId')) {
    localStorage.setItem('userId', userId);
}

console.log('User ID:', userId);

// Загрузка данных пользователя
async function loadUserData() {
    try {
        const response = await fetch(`/api/user/${userId}`);
        if (response.ok) {
            gameData = await response.json();
            updateUI();
        }
    } catch (error) {
        console.error('Load user data error:', error);
        // Оффлайн режим
        gameData = {
            money: 500,
            day: 1,
            energy: 100,
            max_energy: 100,
            current_job: 'delivery',
            trait: null,
            trait_selected: false
        };
        updateUI();
    }
}

// Обновление интерфейса
function updateUI() {
    document.getElementById('day').textContent = gameData.day || 1;
    document.getElementById('money').textContent = gameData.money || 500;
    document.getElementById('moneyProgress').textContent = gameData.money || 500;
    document.getElementById('energy').textContent = gameData.energy || 100;
    
    // Прогресс бары
    const energyPercent = ((gameData.energy || 100) / (gameData.max_energy || 100)) * 100;
    document.getElementById('energyFill').style.width = energyPercent + '%';
    
    const moneyPercent = Math.min(((gameData.money || 500) / 10000) * 100, 100);
    document.getElementById('moneyFill').style.width = moneyPercent + '%';
    
    // Кнопка работать
    const workBtn = document.getElementById('workBtn');
    workBtn.disabled = (gameData.energy || 100) <= 0;
    
    // Персонаж
    const avatar = document.getElementById('characterAvatar');
    if (gameData.energy < 30) {
        avatar.textContent = '😴';
    } else if (gameData.day <= 10) {
        avatar.textContent = '☕';
    } else if (gameData.day <= 20) {
        avatar.textContent = '💻';
    } else {
        avatar.textContent = '🍺';
    }
    
    // Черта
    if (gameData.trait) {
        const traits = {
            'терпила': { emoji: '😤', name: 'Терпила' },
            'рисковый': { emoji: '🎲', name: 'Рисковый' },
            'экономный': { emoji: '💰', name: 'Экономный' },
            'прокрастинатор': { emoji: '😴', name: 'Прокрастинатор' }
        };
        const trait = traits[gameData.trait];
        if (trait) {
            document.getElementById('traitEmoji').textContent = trait.emoji;
            document.getElementById('traitName').textContent = trait.name;
        }
    }
    
    // Текущая работа
    const jobs = {
        'delivery': { name: 'Курьер', income: 80, energy: 5 },
        'office': { name: 'Офис', income: 120, energy: 3 },
        'freelance': { name: 'Фриланс', income: 200, energy: 7 },
        'crypto': { name: 'Крипто', income: 300, energy: 10 }
    };
    
    const currentJob = jobs[gameData.current_job || 'delivery'];
    if (currentJob) {
        document.getElementById('currentJobName').textContent = currentJob.name;
        document.getElementById('jobIncome').textContent = currentJob.income;
        document.getElementById('jobEnergy').textContent = currentJob.energy;
    }
}

// Показать сообщение
function showMessage(text, isSuccess = false) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = 'message' + (isSuccess ? ' success' : '');
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

// Работать
async function work() {
    try {
        const response = await fetch('/api/work', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        
        if (response.ok) {
            const result = await response.json();
            gameData = result.user;
            
            let message = `+${result.income}₽`;
            if (result.event) {
                message += ` | ${result.event.text} ${result.event.cost > 0 ? '+' : ''}${result.event.cost}₽`;
            }
            
            showMessage(message, true);
            updateUI();
            
            // Проверка целей
            if (result.newly_completed_goals && result.newly_completed_goals.length > 0) {
                result.newly_completed_goals.forEach(goal => {
                    setTimeout(() => {
                        showMessage(`🎉 Цель выполнена: ${goal.name}! ${goal.reward_description}`, true);
                    }, 1000);
                });
            }
        } else {
            const error = await response.json();
            showMessage(error.error || 'Ошибка!');
        }
    } catch (error) {
        console.error('Work error:', error);
        showMessage('Ошибка соединения!');
    }
}

// Следующий день
async function nextDay() {
    try {
        const response = await fetch('/api/next_day', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        
        if (response.ok) {
            const result = await response.json();
            gameData = result.user;
            showMessage('Новый день начался! 🌅', true);
            updateUI();
        }
    } catch (error) {
        console.error('Next day error:', error);
        showMessage('Ошибка соединения!');
    }
}

// Показать работы
function showJobs() {
    const jobsList = document.getElementById('jobsList');
    jobsList.innerHTML = '';
    
    const jobs = {
        'delivery': { name: 'Доставка еды', emoji: '🛵', income: 80, energy: 5, unlock_day: 1, desc: 'Быстрые деньги' },
        'office': { name: 'Офисная работа', emoji: '💻', income: 120, energy: 3, unlock_day: 5, desc: 'Стабильный доход' },
        'freelance': { name: 'Фриланс', emoji: '🎨', income: 200, energy: 7, unlock_day: 10, desc: 'Высокий доход' },
        'crypto': { name: 'Крипто-трейдинг', emoji: '📈', income: 300, energy: 10, unlock_day: 15, desc: 'Рискованно' }
    };
    
    Object.keys(jobs).forEach(jobId => {
        const job = jobs[jobId];
        const isUnlocked = gameData.day >= job.unlock_day;
        const isCurrent = gameData.current_job === jobId;
        
        const jobCard = document.createElement('div');
        jobCard.className = `item-card ${!isUnlocked ? 'locked' : ''} ${isCurrent ? 'owned' : ''}`;
        
        if (isUnlocked && !isCurrent) {
            jobCard.onclick = () => changeJob(jobId);
        }
        
        jobCard.innerHTML = `
            <div class="item-header">
                <div class="item-icon">${job.emoji}</div>
                <div class="item-name">${job.name}</div>
                <div class="item-price">+${job.income}₽</div>
            </div>
            <div class="item-desc">${job.desc} | Энергия: -${job.energy}</div>
            <div class="item-desc">${isUnlocked ? (isCurrent ? '✅ Текущая работа' : 'Доступно') : `🔒 Откроется на ${job.unlock_day} день`}</div>
        `;
        
        jobsList.appendChild(jobCard);
    });
    
    document.getElementById('jobsModal').style.display = 'flex';
}

// Сменить работу
async function changeJob(jobId) {
    try {
        const response = await fetch('/api/change_job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, job_id: jobId })
        });
        
        if (response.ok) {
            const result = await response.json();
            gameData = result.user;
            updateUI();
            document.getElementById('jobsModal').style.display = 'none';
            showMessage('Работа изменена!', true);
        }
    } catch (error) {
        console.error('Change job error:', error);
        showMessage('Ошибка!');
    }
}

// Показать магазин
function showShop() {
    const shopList = document.getElementById('shopList');
    shopList.innerHTML = '';
    
    const items = {
        'coffee': { name: 'Кофе', emoji: '☕', price: 150, desc: '+30 энергии' },
        'energy_drink': { name: 'Энергетик', emoji: '🥤', price: 300, desc: '+50 энергии' },
        'laptop': { name: 'Ноутбук', emoji: '💻', price: 2000, desc: 'Офис +50%' },
        'scooter': { name: 'Самокат', emoji: '🛴', price: 1500, desc: 'Доставка -20% энергии' }
    };
    
    Object.keys(items).forEach(itemId => {
        const item = items[itemId];
        const canAfford = gameData.money >= item.price;
        const isOwned = gameData.owned_items && gameData.owned_items.includes(itemId);
        
        const itemCard = document.createElement('div');
        itemCard.className = `item-card ${!canAfford ? 'locked' : ''} ${isOwned ? 'owned' : ''}`;
        
        if (canAfford && !isOwned) {
            itemCard.onclick = () => buyItem(itemId);
        }
        
        itemCard.innerHTML = `
            <div class="item-header">
                <div class="item-icon">${item.emoji}</div>
                <div class="item-name">${item.name}</div>
                <div class="item-price">${item.price}₽</div>
            </div>
            <div class="item-desc">${item.desc}</div>
            <div class="item-desc">${isOwned ? '✅ Куплено' : (canAfford ? 'Доступно' : '🔒 Недостаточно денег')}</div>
        `;
        
        shopList.appendChild(itemCard);
    });
    
    document.getElementById('shopModal').style.display = 'flex';
}

// Купить предмет
async function buyItem(itemId) {
    try {
        const response = await fetch('/api/buy_booster', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, booster_id: itemId })
        });
        
        if (response.ok) {
            const result = await response.json();
            gameData = result.user;
            updateUI();
            showShop();
            showMessage('Куплено!', true);
        }
    } catch (error) {
        console.error('Buy item error:', error);
        showMessage('Ошибка!');
    }
}

// Показать достижения
async function showGoals() {
    try {
        const response = await fetch('/api/goals');
        const goals = await response.json();
        
        const goalsList = document.getElementById('goalsList');
        goalsList.innerHTML = '';
        
        Object.keys(goals).forEach(goalId => {
            const goal = goals[goalId];
            const isCompleted = gameData.completed_goals && gameData.completed_goals.includes(goalId);
            
            const goalCard = document.createElement('div');
            goalCard.className = `achievement-card ${isCompleted ? 'completed' : ''}`;
            
            goalCard.innerHTML = `
                <div class="achievement-icon">${goal.emoji}</div>
                <div class="achievement-info">
                    <div class="achievement-title">${goal.name}</div>
                    <div class="achievement-desc">${goal.description}</div>
                </div>
                <div class="achievement-reward">${isCompleted ? '✅' : `💰+${goal.reward_money}₽`}</div>
            `;
            
            goalsList.appendChild(goalCard);
        });
        
        document.getElementById('goalsModal').style.display = 'flex';
    } catch (error) {
        console.error('Show goals error:', error);
        showMessage('Ошибка загрузки целей!');
    }
}

// Обработчики событий
document.getElementById('workBtn').addEventListener('click', work);
document.getElementById('nextDayBtn').addEventListener('click', nextDay);
document.getElementById('jobsBtn').addEventListener('click', showJobs);
document.getElementById('shopBtn').addEventListener('click', showShop);
document.getElementById('goalsBtn').addEventListener('click', showGoals);

// Закрытие модальных окон
document.getElementById('closeJobsModal').addEventListener('click', () => {
    document.getElementById('jobsModal').style.display = 'none';
});
document.getElementById('closeShopModal').addEventListener('click', () => {
    document.getElementById('shopModal').style.display = 'none';
});
document.getElementById('closeGoalsModal').addEventListener('click', () => {
    document.getElementById('goalsModal').style.display = 'none';
});

// Загрузка при старте
loadUserData();
