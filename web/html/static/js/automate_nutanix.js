class Ajax {
    static get(url, success, fail) {
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
        }).done(function (data) {
            success(data)
        }).fail(function (data) {
            fail(data)
        })
    }

    static post(url, json, success, fail) {
        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify(json)
        }).done(function (data) {
            success(data)
        }).fail(function (data) {
            fail(data)
        })
    }

    static put(url, json, success, fail) {
        $.ajax({
            url: url,
            type: 'PUT',
            dataType: 'json',
            data: JSON.stringify(json)
        }).done(function (data) {
            success(data)
        }).fail(function (data) {
            fail(data)
        })
    }

    static delete(url, success, fail) {
        $.ajax({
            url: url,
            type: 'DELETE',
            dataType: 'json',
        }).done(function (data) {
            success(data)
        }).fail(function (data) {
            fail(data)
        })
    }
}

class IndexPage {
    
    static updateClusterTable(){
        const url = "/api/public/cluster/v1/clusters_status/"
        Ajax.get(url, IndexPage.getStatusSuccess, IndexPage.getStatusFail)
    }

    static getStatusSuccess(data){
        $("#cluster_table").empty()
        let hrow = '<tr><th>Name</th><th>IPMI Mac</th><th>IPMI IP</th><th>Host IP</th><th>CVM IP</th>'
        hrow += '<th>Cluster IP</th><th>Credential</th><th>Actions</th><th></th></tr>'
        $("#cluster_table").append(hrow)

        const existFilter = function(v){
            return v.exist
        }
        for(let cluster of data){
            const name = cluster.name

            if(!cluster.success){
                let row = `<tr><td>${name}</td><td>-</td><td>-</td><td>-</td><td>-</td>`
                row += `<td>-</td><td>-</td>`
                row += `<td>please check fvms</td><td>${cluster.fvms}</td></tr>`
                $("#cluster_table").append(row)
                continue
            }
            
            const ipmi_mac = cluster.ipmi_mac_status.filter(existFilter).length + '/' + cluster.ipmi_mac_status.length
            const ipmi_ip = cluster.ipmi_ip_status.filter(existFilter).length + '/' + cluster.ipmi_ip_status.length
            const host_ip = cluster.host_ip_status.filter(existFilter).length + '/' + cluster.host_ip_status.length
            const cvm_ip = cluster.cvm_ip_status.filter(existFilter).length + '/' + cluster.cvm_ip_status.length
            const prism_ip = cluster.prism_ip_status
            const prism_credential_status = cluster.prism_credential_status
            
            let foundation_button = '<div class="dropdown">'
            foundation_button += '  <button class="btn btn-danger dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'
            foundation_button += '    Foundation'
            foundation_button += '  </button>'
            foundation_button += '  <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">'
            for(let image of cluster.fvm_images){
                foundation_button += `    <a class="dropdown-item" href="javascript:void(0);" onclick="IndexPage.doFoundationAll('${cluster.uuid}','${image}');">${image}</a>`
            }
            foundation_button += '  </div>'
            foundation_button += '</div>'

            const poweron_button = `<button type="button" class="btn btn-secondary" onclick="IndexPage.doPowerOn('${cluster.uuid}')">PowerOn</button>`
            const poweroff_button = `<button type="button" class="btn btn-secondary" onclick="IndexPage.doPowerOff('${cluster.uuid}')">PowerOff</button>`

            let row = `<tr><td>${name}</td><td>${ipmi_mac}</td><td>${ipmi_ip}</td><td>${host_ip}</td><td>${cvm_ip}</td>`
            row += `<td>${prism_ip}</td><td>${prism_credential_status}</td>`
            row += `<td>${foundation_button}</td><td>${poweron_button} ${poweroff_button}</td></tr>`
            $("#cluster_table").append(row)
        }
    }

    static getStatusFail(data){
        console.log('getting cluster status fail')
    }

    static getCluster(uuid){

    }

    static getClusterSuccess(data){

    }

    static doFoundationAll(uuid, image){
        const successAction = function(data){
            alert('start foundation. task uuid:' + data['uuid'])
        }
        const failAction = function(data){
            console.log('failed to call foundation@bulkapi')
        }
        const successGetCluster = function(data){
            const url = "/api/public/bulkactions/v1/foundation"
            data.foundation = {'aos_version':image}
            console.log(data)
            Ajax.post(url, data, successAction, failAction)
        }
        const failGetCluster = function(data){
            console.log('failed to get cluster info')
        }

        const url = "/api/public/cluster/v1/clusters/" + uuid
        Ajax.get(url, successGetCluster, failGetCluster)
    }

    static doFoundation(uuid, image){

    }

    static doEula(uuid){

    }

    static doSetup(uuid){

    }

    static doPowerOn(uuid){
        const successAction = function(data){
            alert('start power-on. task uuid:' + data['uuid'])
        }
        const failAction = function(data){
            console.log('failed to call poweron @ power api')
        }
        const successGetCluster = function(data){
            const url = "/api/public/power/v1/on"
            Ajax.post(url, data, successAction, failAction)
        }
        const failGetCluster = function(data){
            console.log('failed to get cluster info')
        }

        const url = "/api/public/cluster/v1/clusters/" + uuid
        Ajax.get(url, successGetCluster, failGetCluster)
    }

    static doPowerOff(uuid){
        const successAction = function(data){
            alert('start power-off. task uuid:' + data['uuid'])
        }
        const failAction = function(data){
            console.log('failed to call poweron @ power api')
        }
        const successGetCluster = function(data){
            const url = "/api/public/power/v1/off"
            Ajax.post(url, data, successAction, failAction)
        }
        const failGetCluster = function(data){
            console.log('failed to get cluster info')
        }

        const url = "/api/public/cluster/v1/clusters/" + uuid
        Ajax.get(url, successGetCluster, failGetCluster)
    }
}

const _TaskPage = {
    'tasks': {}
}

class TaskPage {

    static updateTaskTable(){
        $("#primary_table").empty()
        $("#child_table").empty()
        let hrow = '<tr><th>Name</th><th>UUID</th><th>Parent UUID</th><th>Owner</th><th>Progress</th><th>Finished</th><th>Success</th>'
        hrow += '<th>Start</th><th>End</th><th>Log</th></tr>'
        $("#primary_table").append(hrow)
        $("#child_table").append(hrow)

        for(let task_key in _TaskPage.tasks){
            const task = _TaskPage.tasks[task_key]
            const name = task.name
            const uuid = task.uuid
            const parent_uuid = task.parent_uuid
            const owner = task.owner
            const progress = task.progress
            const finished = task.finished
            const success = task.success
            const start = task.timestamp_start
            const end = task.timestamp_end
            const log = `<a href="/log.html?owner=${owner}&uuid=${uuid}" target="_blank">Open Viewr</a>`

            let row = `<tr><td>${name}</td><td>${uuid}</td><td>${parent_uuid}</td><td>${owner}</td><td>-</td><td>${finished}</td>`
            row += `<td>${success}</td><td>${start}</td><td>${end}</td><td>${log}</td></tr>`
            if(parent_uuid == ""){
                $("#primary_table").append(row)
            }else{
                $("#child_table").append(row)
            }
        }
    }

    static collectTasksStatus(){
        TaskPage.getBulkActionTasks()
        TaskPage.getFoundationTasks()
        TaskPage.getEulaTasks()
        TaskPage.getSetupTasks()
        TaskPage.getPowerTasks()
    }

    static registerTasks(owner, tasks){
        for(let task of tasks){
            task['owner'] = owner
            _TaskPage.tasks[task.uuid] = task
        }
    }

    static getBulkActionTasks(){
        const success = function(data){
            TaskPage.registerTasks('bulkactions', data)
        }
        const fail = function(data){
            console.log('getBulkActionTasks() failed')
        }
        const url = "/api/public/bulkactions/v1/tasks/"
        Ajax.get(url, success, fail)
    }

    static getFoundationTasks(){
        const success = function(data){
            TaskPage.registerTasks('foundation', data)
        }
        const fail = function(data){
            console.log('getFoundationTasks() failed')
        }
        const url = "/api/public/foundation/v1/tasks/"
        Ajax.get(url, success, fail)
    }

    static getEulaTasks(){
        const success = function(data){
            TaskPage.registerTasks('eula', data)
        }
        const fail = function(data){
            console.log('getEulaTasks() failed')
        }
        const url = "/api/public/eula/v1/tasks/"
        Ajax.get(url, success, fail)
    }

    static getSetupTasks(){
        const success = function(data){
            TaskPage.registerTasks('setup', data)
        }
        const fail = function(data){
            console.log('getSetupTasks() failed')
        }
        const url = "/api/public/setup/v1/tasks/"
        Ajax.get(url, success, fail)
    }

    static getPowerTasks(){
        const success = function(data){
            TaskPage.registerTasks('power', data)
        }
        const fail = function(data){
            console.log('getPowerTasks() failed')
        }
        const url = "/api/public/power/v1/tasks/"
        Ajax.get(url, success, fail)   
    }

}

class TaskLogPage {

    static getUrlParam(name) {
        const url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return '';
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }

    static updateLog(){
        const success = function(data){
            // update log
            const log = data.log
            $("#log_textarea").text(log)

            /*
            // scroll to bottom of the page
            const element = document.documentElement;
            const bottom = element.scrollHeight - element.clientHeight;
            window.scroll(0, bottom);
            */
        }
        const fail = function(data){
            $("#log_textarea").text('getting log failed')
        }

        const owner = TaskLogPage.getUrlParam('owner')
        const uuid = TaskLogPage.getUrlParam('uuid')
        const url = `/api/public/${owner}/v1/tasks/${uuid}`
        Ajax.get(url, success, fail)
    }
}