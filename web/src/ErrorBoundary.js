import React from 'react';

class ErrorBoundary extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			hasError: false,
		};
	}

	componentDidCatch(error, info) {
		console.log(error, info.componentStack);
		this.setState({ hasError: true });
	}

	render() {
		const { hasError } = this.state;
		const { children, goBack } = this.props;
		if (hasError) {
			return (
				<div className="error_block">
					<span>Ошибка приложения</span>
					<span className="btn" onClick={() => { goBack(); document.location.reload(); }}>Обновить</span>
				</div>
			);
		}
		if (!hasError) {
			return (
				children
			);
		}
	}
}

export default ErrorBoundary;
