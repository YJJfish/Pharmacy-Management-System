//Add item x1 to the shopping cart
function AddItem(UserID, BranchName, MediID, MediBrand, MediName){
    function addShoppingCart(UserID, MediID, BranchName, Num){
        return true;
    }
    /*Call database*/
    Ret = addShoppingCart(UserID, MediID, BranchName, 1);
    if (Ret){
        alert("成功向购物车添加药品 " + MediName + "(" + MediID + " " + MediBrand + ")一份，院区：" + BranchName + ".");
    }else{
        alert("药品添加失败 " + MediName + "(" + MediID + " " + MediBrand + ")，院区：" + BranchName + "。请刷新页面");
        location.reload();
    }
}

//Commit the current bill
function Checkout(UserID, BranchName, Redirection){
    function commitBill(UserID, BranchName){
        return true;
    }
    Ret = commitBill(UserID, BranchName);
    if (Ret == false)
        alert("服务器内部错误");
    //Redirect
    location = Redirection;
}

function SetItem(BillID, UserID, MediID, BranchName, Num){
    function setShoppingCart(UserID, MediID, BranchName, Num){
        return true;
    }
    /*Call database*/
    Ret = setShoppingCart(UserID, MediID, BranchName, Num);
    if (Ret){
        //Get the corresponding element that displays sum
        SumEle = document.getElementById(BillID+"_Sum");
        //Get the element corresponding to this bill
        BillEle = document.getElementById(BillID+"_Products");
        //Get the element corresponding to the checkout button
        CheckoutEle = document.getElementById(BillID+"_Checkout");
        //If Num==0, delete the product
        if (Num == 0){
            Div = document.getElementById(BillID+"_"+MediID);
            BillEle.removeChild(Div);
        }
        //Update sum
        Sum = 0
        for(var i = 0; i < BillEle.children.length; i++){
            Quantity = document.getElementById(BillEle.children[i].id+"_Quantity");
            Price = document.getElementById(BillEle.children[i].id+"_Price");
            Sum += Quantity.value*Price.innerHTML.substr(1);
        }
        SumEle.innerHTML = "总价: ￥"+Sum.toFixed(2);
        //Enable or disable the checkout button
        if (Sum == 0)
            CheckoutEle.setAttribute("disabled", "");
        else
            CheckoutEle.removeAttribute("disabled");
    }else{
        alert("无法修改该药品数量。请刷新界面.");
        location.reload();
    }
}