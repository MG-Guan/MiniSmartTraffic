<!--cd traffic_light-->
<!--npm run serve-->
<template>
  <div>
    <!-- 固定标题 -->
    <div class="header">
      Smart Traffic Light System
    </div>

    <!-- 主体区域（左右布局） -->
    <div class="app-container">
      <div class="sidebar">
        <div class="status">
          <p>
            <strong>Traffic Light Status:</strong>
            <span :style="{ color: statusColor }">{{ trafficStatus }}</span>
            <span class="dot" :style="{ backgroundColor: statusColor }"></span>
          </p>
          <p><strong>Last Update:</strong> {{ lastUpdate }}</p>
          <p><strong>Connectivity:</strong> <span class="connected">Connected</span></p>
        </div>

        <hr />

        <div class="control">
          <h3>Control</h3>
          <button
            v-for="cmd in commands"
            :key="cmd"
            @click="handleControl(cmd)"
          >
            {{ cmd }}
          </button>
        </div>
      </div>

      <!-- 右侧主区域 -->
      <div class="main-content">
            <ViolationList />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ViolationList from './ViolationList.vue'

const trafficStatus = ref('Red')
const lastUpdate = ref('2025-06-05 00:00:00')
const commands = ['Red', 'Green', 'Flashing Red', 'Flashing Yellow', 'Constant Red', 'Constant Green']

const statusColor = computed(() => {
  switch (trafficStatus.value) {
    case 'Red': return 'red'
    case 'Green': return 'green'
    case 'Flashing Red': return 'orange'
    case 'Flashing Yellow': return 'gold'
    case 'Constant Red': return 'darkred'
    case 'Constant Green': return 'darkgreen'
    default: return 'gray'
  }
})

function handleControl(cmd) {
  console.log('Control command sent:', cmd)
  // TODO: 将来这里用 axios.post('/api/control', { command: cmd })
}

</script>


<style scoped>

button.active {
  background-color: #007bff;
  color: white;
}

.page-input {
  width: 60px;
  padding: 4px;
  border: 1px solid #aaa;
  border-radius: 4px;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background-color: #333;
  color: white;
  font-size: 20px;
  font-weight: bold;
  padding: 10px 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
}

/* 主体区下移避免被标题遮住 */
.app-container {
  display: flex;
  padding-top: 50px; /* 避免被顶部标题遮住 */
  height: calc(100vh - 50px);
}

.sidebar {
  width: 250px;
  padding: 20px;
  border-right: 1px solid #ccc;
  background-color: #f9f9f9;
  /* 修改这里：不要 space-between，只让元素正常竖排 */
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.status p {
  margin: 6px 0;
}

.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-left: 6px;
  border-radius: 50%;
  vertical-align: middle;
}

.connected {
  color: green;
  font-weight: bold;
}

.control {
  margin-top: 20px;
  display: flex;
  flex-direction: column; /* ✅ 按钮竖直排列 */
  gap: 10px;
}

.control button {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #888;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
}

.control button:hover {
  background-color: #eee;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>


