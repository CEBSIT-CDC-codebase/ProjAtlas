/**
 * Web Worker pool manager
 * Manages a set of Worker instances to avoid performance issues from creating too many Workers
 */
class WorkerPool {
  /**
   * Create the Worker pool
   * @param {String} scriptUrl URL of the Worker script
   * @param {Number} size Number of Workers in the pool
   */
  constructor(scriptUrl, size = 4) {
    this.scriptUrl = scriptUrl;
    this.size = size;
    this.workers = [];
    this.freeWorkers = [];
    this.taskQueue = [];
    this.taskMap = new Map(); // Stores the mapping between task IDs and callbacks
    this.taskIdCounter = 0;

    this.init();
  }

  /**
   * Initialize the Worker pool
   */
  init() {
    // Create the specified number of Workers
    for (let i = 0; i < this.size; i++) {
      const worker = new Worker(this.scriptUrl);

      // Set up the message handler
      worker.onmessage = event => {
        // Handle the Worker's response
        this.handleWorkerMessage(worker, event.data);
      };

      // Handle errors
      worker.onerror = error => {
        console.error("Worker error:", error);
        // Return the Worker to the pool
        this.freeWorkers.push(worker);
        // Process the next task
        this.processNextTask();
      };

      // Add the Worker to the pool
      this.workers.push(worker);
      this.freeWorkers.push(worker);
    }
  }

  /**
   * Handle a Worker's response message
   * @param {Worker} worker The Worker that sent the message
   * @param {*} data Data returned by the Worker
   */
  handleWorkerMessage(worker, data) {
    // Look up the callback info by task ID
    const taskInfo = this.taskMap.get(data.taskId);

    if (taskInfo) {
      // Invoke the callback to handle the result
      taskInfo.resolve(data.result);

      // Remove the task from the map
      this.taskMap.delete(data.taskId);

      // Return the Worker to the free pool
      this.freeWorkers.push(worker);

      // Process the next queued task
      this.processNextTask();
    }
  }

  /**
   * Process the next task in the queue
   */
  processNextTask() {
    // If there are pending tasks and free Workers available
    if (this.taskQueue.length > 0 && this.freeWorkers.length > 0) {
      // Get a task and a free Worker
      const task = this.taskQueue.shift();
      const worker = this.freeWorkers.pop();

      // Send the task to the Worker
      worker.postMessage({
        taskId: task.taskId,
        data: task.data,
        context: task.context
      });
    }
  }

  /**
   * Run a task
   * @param {*} data Data to process
   * @param {*} context Task context info (optional)
   * @returns {Promise} A Promise that resolves with the task result
   */
  runTask(data, context = null) {
    return new Promise(resolve => {
      // Create a task ID
      const taskId = this.taskIdCounter++;

      // Create the task object
      const task = {
        taskId,
        data,
        context,
        resolve
      };

      // Store the task callback info
      this.taskMap.set(taskId, task);

      // Add the task to the queue
      this.taskQueue.push(task);

      // Try to process the task
      this.processNextTask();
    });
  }

  /**
   * Terminate all Workers
   */
  terminate() {
    // Terminate all Workers
    this.workers.forEach(worker => worker.terminate());

    // Clear all arrays and maps
    this.workers = [];
    this.freeWorkers = [];
    this.taskQueue = [];
    this.taskMap.clear();
  }
}

export default WorkerPool;
