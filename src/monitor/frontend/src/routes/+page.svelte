<script>
    import { onMount } from "svelte";

    let interval = 0;
    let failed_messages = 0;
    let success_messages = 0;
    let average_delay = 0.0;
    
    onMount(async () => {
        while (interval == 0) {
            let res = await fetch("http://localhost:8000/interval");
            let interval_obj = await res.json()
    
            interval = interval_obj.interval;
        }


        setInterval(async () => {
            let stat_res = await fetch("http://localhost:8000/statistics");
            let stat_obj = await stat_res.json();

            failed_messages = stat_obj.failed_messages;
            success_messages = stat_obj.success_messages;
            average_delay = stat_obj.average_delay;
        }, interval * 1000)
    });
</script>

<div class="bg-blue-400 w-full min-w-full py-10 mb-10 border-b-4 border-b-black">
    <h1 class="text-5xl font-bold">SMS Simulator Progress Monitor</h1>
</div>
<div class="grid grid-cols-3 justify-items-center">
    <div class="text-center ml-10 mb-10 min-w-[300px] max-w-[400px] min-h-[120px] border-black border-4 bg-blue-200">
        <h2 class="text-2xl font-bold">Sent Messages</h2>
        <h2 class="text-6xl font-bold">{success_messages}</h2>
    </div>
    <div class="text-center ml-10 mb-10 min-w-[300px] max-w-[400px] min-h-[120px] border-black border-4 bg-blue-200">
        <h2 class="text-2xl font-bold">Failed Messages</h2>
        <h2 class="text-6xl font-bold">{failed_messages}</h2>
    </div>
    <div class="text-center ml-10 mb-10 min-w-[300px] max-w-[400px] min-h-[120px] border-black border-4 bg-blue-200">
        <h2 class="text-2xl font-bold">Average Delay</h2>
        <h2 class="text-6xl font-bold">{average_delay+"s"}</h2>
    </div>
</div>
<div class="bg-slate-400 text-center text-s"><span>{"Updated Every " + interval + " second(s)"}</span></div>